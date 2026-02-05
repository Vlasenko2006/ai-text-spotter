#!/usr/bin/env python3
"""
Automated Iterative Tuning Script for AI Text Detector
Analyzes example texts, evaluates performance, and tunes parameters until confident detection.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import urllib.request
import urllib.parse


class AutoTuner:
    def __init__(self, api_url="http://localhost/api", examples_dir="examples"):
        self.api_url = api_url
        self.examples_dir = Path(examples_dir)
        self.iteration = 0
        self.max_iterations = 10
        
        # Ground truth labels
        self.ground_truth = {
            "human_written.txt": "human",
            "ai_generated.txt": "ai",
            "mixed.txt": "mixed"
        }
        
        # Current detector parameters (will be adjusted)
        self.params = {
            "math_bias": 0.10,  # Bias added to mathematical detector
            "llm_bias": 0.20,   # Bias added to LLM detector
            "human_threshold": 0.50,  # Score above = human
            "ai_threshold": 0.35,     # Score below = ai
            "math_weight_low_llm": 0.60,  # Math weight when LLM < 0.25
            "math_weight_high_llm": 0.60,  # Math weight when LLM > 0.60
            "math_weight_uncertain": 0.85  # Math weight when LLM 0.25-0.60
        }
        
        # Performance tracking
        self.history = []
        
    def load_test_files(self) -> Dict[str, str]:
        """Load all .txt test files."""
        files = {}
        for file_path in self.examples_dir.glob("*.txt"):
            if file_path.name == "README.md":
                continue
            with open(file_path, 'r', encoding='utf-8') as f:
                files[file_path.name] = f.read()
        return files
    
    def analyze_text(self, text: str) -> Dict:
        """Send text to API for analysis."""
        try:
            data = json.dumps({"text": text}).encode('utf-8')
            req = urllib.request.Request(
                f"{self.api_url}/analyze",
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=120) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def evaluate_result(self, filename: str, result: Dict) -> Dict:
        """Evaluate detection accuracy for a file."""
        if not result or "sentences" not in result:
            return {"accuracy": 0, "total": 0, "correct": 0, "error": "No result"}
        
        expected = self.ground_truth.get(filename, "unknown")
        sentences = result["sentences"]
        
        if len(sentences) == 0:
            return {"accuracy": 0, "total": 0, "correct": 0, "error": "No sentences"}
        
        # Count classifications
        classifications = {"human": 0, "suspicious": 0, "ai": 0}
        for sent in sentences:
            classifications[sent["classification"]] += 1
        
        total = len(sentences)
        
        # Determine dominant classification
        if expected == "mixed":
            # For mixed text, expect a good mix (not all one type)
            dominant = max(classifications, key=classifications.get)
            dominant_pct = classifications[dominant] / total
            # Good if no single category dominates > 70%
            accuracy = 1.0 - max(0, dominant_pct - 0.7) / 0.3
            correct = int(accuracy * total)
        else:
            # For pure human/AI, expect that classification to dominate
            correct = classifications[expected]
            accuracy = correct / total
        
        return {
            "accuracy": accuracy,
            "total": total,
            "correct": correct,
            "classifications": classifications,
            "expected": expected,
            "stats": result.get("overall_stats", {})
        }
    
    def get_docker_logs(self, lines=50) -> str:
        """Get recent docker logs."""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), "ai-text-spotter-backend"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout + result.stderr
        except Exception as e:
            return f"Error getting logs: {e}"
    
    def adjust_parameters(self, results: List[Dict]) -> bool:
        """Adjust parameters based on results. Returns True if changes made."""
        # Calculate overall accuracy
        total_acc = sum(r["accuracy"] for r in results) / len(results) if results else 0
        
        # Analyze specific issues
        human_file = next((r for r in results if r.get("filename") == "human_written.txt"), None)
        ai_file = next((r for r in results if r.get("filename") == "ai_generated.txt"), None)
        
        changes = []
        
        # If human text is being flagged as AI (low accuracy for human)
        if human_file and human_file["accuracy"] < 0.7:
            if human_file["classifications"]["ai"] > human_file["classifications"]["human"]:
                # System is too strict - increase bias toward human
                old_math = self.params["math_bias"]
                self.params["math_bias"] = min(0.25, self.params["math_bias"] + 0.03)
                changes.append(f"Math bias: {old_math:.2f} → {self.params['math_bias']:.2f} (human text flagged as AI)")
                
                old_llm = self.params["llm_bias"]
                self.params["llm_bias"] = min(0.35, self.params["llm_bias"] + 0.03)
                changes.append(f"LLM bias: {old_llm:.2f} → {self.params['llm_bias']:.2f}")
        
        # If AI text is being classified as human (low accuracy for AI)
        if ai_file and ai_file["accuracy"] < 0.7:
            if ai_file["classifications"]["human"] > ai_file["classifications"]["ai"]:
                # System is too lenient - decrease bias toward human
                old_math = self.params["math_bias"]
                self.params["math_bias"] = max(0.0, self.params["math_bias"] - 0.03)
                changes.append(f"Math bias: {old_math:.2f} → {self.params['math_bias']:.2f} (AI text flagged as human)")
                
                old_llm = self.params["llm_bias"]
                self.params["llm_bias"] = max(0.05, self.params["llm_bias"] - 0.03)
                changes.append(f"LLM bias: {old_llm:.2f} → {self.params['llm_bias']:.2f}")
        
        # Adjust thresholds based on overall performance
        if total_acc < 0.6:
            # If overall accuracy is low, adjust thresholds
            old_human = self.params["human_threshold"]
            old_ai = self.params["ai_threshold"]
            
            # Make thresholds more balanced
            gap = self.params["human_threshold"] - self.params["ai_threshold"]
            if gap < 0.10:
                self.params["human_threshold"] = min(0.60, self.params["human_threshold"] + 0.02)
                self.params["ai_threshold"] = max(0.25, self.params["ai_threshold"] - 0.02)
                changes.append(f"Thresholds: human {old_human:.2f}→{self.params['human_threshold']:.2f}, ai {old_ai:.2f}→{self.params['ai_threshold']:.2f}")
        
        return len(changes) > 0, changes
    
    def update_detector_files(self):
        """Update detector Python files with new parameters."""
        # Update mathematical detector
        math_file = Path("backend/app/detectors/mathematical.py")
        with open(math_file, 'r') as f:
            content = f.read()
        
        # Replace bias value
        import re
        content = re.sub(
            r'human_score \+= (0\.\d+)  # Calibration bias',
            f'human_score += {self.params["math_bias"]:.2f}  # Calibration bias',
            content
        )
        
        with open(math_file, 'w') as f:
            f.write(content)
        
        # Update LLM detector
        llm_file = Path("backend/app/detectors/llm_detector.py")
        with open(llm_file, 'r') as f:
            content = f.read()
        
        content = re.sub(
            r'human_score \+= (0\.\d+)  # Calibration bias',
            f'human_score += {self.params["llm_bias"]:.2f}  # Calibration bias',
            content
        )
        
        with open(llm_file, 'w') as f:
            f.write(content)
        
        # Update jury detector thresholds
        jury_file = Path("backend/app/detectors/jury.py")
        with open(jury_file, 'r') as f:
            content = f.read()
        
        # Update thresholds in fallback decision
        content = re.sub(
            r'if weighted_score > (0\.\d+):  # Raised to be more selective',
            f'if weighted_score > {self.params["human_threshold"]:.2f}:  # Raised to be more selective',
            content
        )
        content = re.sub(
            r'elif weighted_score < (0\.\d+):  # Raised to catch more AI',
            f'elif weighted_score < {self.params["ai_threshold"]:.2f}:  # Raised to catch more AI',
            content
        )
        
        with open(jury_file, 'w') as f:
            f.write(content)
        
        print(f"  📝 Updated detector files with new parameters")
    
    def rebuild_container(self):
        """Rebuild Docker container with updated code."""
        print(f"  🔨 Rebuilding backend container...")
        try:
            result = subprocess.run(
                ["/usr/local/bin/docker-compose", "build", "backend"],
                cwd="/Users/andreyvlasenko/tst/ai-text-spotter",
                capture_output=True,
                timeout=120,
                env={"GROQ_API_KEY": "your_api_key_here", "PATH": "/usr/local/bin:/usr/bin:/bin"}
            )
            if result.returncode != 0:
                print(f"  ⚠️ Build stderr: {result.stderr.decode()[:200]}")
            
            print(f"  🚀 Restarting services...")
            result = subprocess.run(
                ["/usr/local/bin/docker-compose", "up", "-d"],
                cwd="/Users/andreyvlasenko/tst/ai-text-spotter",
                capture_output=True,
                timeout=30,
                env={"GROQ_API_KEY": "your_api_key_here", "PATH": "/usr/local/bin:/usr/bin:/bin"}
            )
            print(f"  ⏳ Waiting 10s for services to start...")
            time.sleep(10)
            return True
        except Exception as e:
            print(f"  ❌ Rebuild failed: {e}")
            return False
    
    def run_iteration(self) -> Tuple[float, List[Dict]]:
        """Run one iteration of testing."""
        self.iteration += 1
        print(f"\n{'='*80}")
        print(f"🔄 ITERATION {self.iteration}/{self.max_iterations}")
        print(f"{'='*80}")
        print(f"📊 Current Parameters:")
        for key, value in self.params.items():
            print(f"   {key}: {value}")
        print()
        
        # Load test files
        files = self.load_test_files()
        print(f"📁 Loaded {len(files)} test files: {', '.join(files.keys())}\n")
        
        # Analyze each file
        results = []
        for filename, text in files.items():
            print(f"🔍 Analyzing {filename}...")
            result = self.analyze_text(text)
            
            if result:
                eval_result = self.evaluate_result(filename, result)
                eval_result["filename"] = filename
                results.append(eval_result)
                
                # Print summary
                acc = eval_result["accuracy"] * 100
                emoji = "✅" if acc >= 70 else "⚠️" if acc >= 50 else "❌"
                print(f"   {emoji} Accuracy: {acc:.1f}% ({eval_result['correct']}/{eval_result['total']})")
                print(f"   Expected: {eval_result['expected']}")
                print(f"   Classifications: {eval_result['classifications']}")
            else:
                print(f"   ❌ Analysis failed")
            print()
        
        # Calculate overall accuracy
        overall_acc = sum(r["accuracy"] for r in results) / len(results) if results else 0
        
        # Store in history
        self.history.append({
            "iteration": self.iteration,
            "accuracy": overall_acc,
            "params": self.params.copy(),
            "results": results
        })
        
        return overall_acc, results
    
    def save_report(self):
        """Save final tuning report."""
        report_path = Path("tuning_report.json")
        with open(report_path, 'w') as f:
            json.dump({
                "iterations": self.iteration,
                "final_params": self.params,
                "history": self.history
            }, f, indent=2)
        print(f"\n📄 Full report saved to: {report_path}")
    
    def run(self):
        """Main tuning loop."""
        print("🚀 Starting Automated Tuning Process")
        print(f"   Max iterations: {self.max_iterations}")
        print(f"   Target accuracy: 70%+")
        
        converged = False
        
        while self.iteration < self.max_iterations and not converged:
            # Run iteration
            accuracy, results = self.run_iteration()
            
            # Check logs
            print(f"📋 Recent Docker Logs:")
            logs = self.get_docker_logs(30)
            jury_lines = [l for l in logs.split('\n') if 'Jury decision' in l or 'Groq' in l]
            for line in jury_lines[-10:]:
                print(f"   {line}")
            print()
            
            # Evaluate performance
            print(f"{'='*80}")
            print(f"📈 ITERATION {self.iteration} RESULTS:")
            print(f"   Overall Accuracy: {accuracy*100:.1f}%")
            
            if accuracy >= 0.70:
                print(f"   🎉 TARGET ACHIEVED!")
                converged = True
            else:
                print(f"   📉 Below target (70%), adjusting parameters...")
                
                # Adjust parameters
                changed, changes = self.adjust_parameters(results)
                
                if changed:
                    print(f"\n🔧 Parameter Adjustments:")
                    for change in changes:
                        print(f"   • {change}")
                    
                    # Update files and rebuild
                    self.update_detector_files()
                    if not self.rebuild_container():
                        print("   ⚠️ Rebuild failed, stopping...")
                        break
                else:
                    print(f"   ℹ️ No parameter changes needed")
            
            print(f"{'='*80}\n")
        
        # Final summary
        print(f"\n{'='*80}")
        print(f"🏁 TUNING COMPLETE")
        print(f"{'='*80}")
        print(f"Total Iterations: {self.iteration}")
        print(f"Final Accuracy: {accuracy*100:.1f}%")
        print(f"Status: {'✅ Converged' if converged else '⚠️ Max iterations reached'}")
        print(f"\n📊 Final Parameters:")
        for key, value in self.params.items():
            print(f"   {key}: {value}")
        
        self.save_report()
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Review tuning_report.json for detailed history")
        print(f"   2. Test with your own cover letters")
        print(f"   3. Fine-tune manually if needed")


if __name__ == "__main__":
    tuner = AutoTuner()
    tuner.run()
