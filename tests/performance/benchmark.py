"""
Performance Benchmarking Suite for OpenManus-Youtu Integrated Framework
Comprehensive benchmarking and performance analysis
"""

import asyncio
import time
import statistics
import json
import psutil
import os
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

from src.api.server import create_app
from src.agents.simple_agent import SimpleAgent
from src.agents.browser_agent import BrowserAgent
from src.agents.orchestra_agent import OrchestraAgent
from src.agents.meta_agent import MetaAgent
from src.tools.base_tool import BaseTool
from src.tools.web_tools import WebScrapingTool
from src.tools.search_tools import WebSearchTool
from src.tools.analysis_tools import DataAnalysisTool


@dataclass
class BenchmarkResult:
    """Benchmark result data class."""
    name: str
    duration: float
    success: bool
    memory_usage: float
    cpu_usage: float
    throughput: float
    error_message: str = None


class PerformanceBenchmark:
    """Performance benchmarking suite."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process(os.getpid())

    async def benchmark_agent_creation(self, num_agents: int = 100) -> BenchmarkResult:
        """Benchmark agent creation performance."""
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu = self.process.cpu_percent()
        
        agents = []
        try:
            for i in range(num_agents):
                agent = SimpleAgent(
                    name=f"benchmark_agent_{i}",
                    config={"max_iterations": 5}
                )
                agents.append(agent)
            
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024
            end_cpu = self.process.cpu_percent()
            
            duration = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = end_cpu - start_cpu
            throughput = num_agents / duration
            
            return BenchmarkResult(
                name="Agent Creation",
                duration=duration,
                success=True,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                throughput=throughput
            )
        except Exception as e:
            return BenchmarkResult(
                name="Agent Creation",
                duration=time.time() - start_time,
                success=False,
                memory_usage=0,
                cpu_usage=0,
                throughput=0,
                error_message=str(e)
            )

    async def benchmark_agent_execution(self, num_executions: int = 100) -> BenchmarkResult:
        """Benchmark agent execution performance."""
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu = self.process.cpu_percent()
        
        try:
            agent = SimpleAgent(name="benchmark_execution_agent")
            
            # Execute tasks
            tasks = []
            for i in range(num_executions):
                task = agent.execute_task(
                    task=f"Calculate {i + 1} * 2",
                    parameters={"number": i + 1, "multiplier": 2}
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024
            end_cpu = self.process.cpu_percent()
            
            duration = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = end_cpu - start_cpu
            throughput = num_executions / duration
            
            return BenchmarkResult(
                name="Agent Execution",
                duration=duration,
                success=True,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                throughput=throughput
            )
        except Exception as e:
            return BenchmarkResult(
                name="Agent Execution",
                duration=time.time() - start_time,
                success=False,
                memory_usage=0,
                cpu_usage=0,
                throughput=0,
                error_message=str(e)
            )

    async def benchmark_tool_execution(self, num_executions: int = 100) -> BenchmarkResult:
        """Benchmark tool execution performance."""
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu = self.process.cpu_percent()
        
        try:
            tool = DataAnalysisTool()
            
            # Execute tool multiple times
            tasks = []
            for i in range(num_executions):
                task = tool.run(
                    data=list(range(1, i + 6)),
                    analysis_type="descriptive"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024
            end_cpu = self.process.cpu_percent()
            
            duration = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = end_cpu - start_cpu
            throughput = num_executions / duration
            
            return BenchmarkResult(
                name="Tool Execution",
                duration=duration,
                success=True,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                throughput=throughput
            )
        except Exception as e:
            return BenchmarkResult(
                name="Tool Execution",
                duration=time.time() - start_time,
                success=False,
                memory_usage=0,
                cpu_usage=0,
                throughput=0,
                error_message=str(e)
            )

    async def benchmark_concurrent_operations(self, num_operations: int = 50) -> BenchmarkResult:
        """Benchmark concurrent operations performance."""
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu = self.process.cpu_percent()
        
        try:
            # Create multiple agents and execute tasks concurrently
            agents = []
            for i in range(num_operations):
                agent = SimpleAgent(name=f"concurrent_agent_{i}")
                agents.append(agent)
            
            # Execute tasks concurrently
            tasks = []
            for i, agent in enumerate(agents):
                task = agent.execute_task(
                    task=f"Calculate {i + 1} * 3",
                    parameters={"number": i + 1, "multiplier": 3}
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024
            end_cpu = self.process.cpu_percent()
            
            duration = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = end_cpu - start_cpu
            throughput = num_operations / duration
            
            return BenchmarkResult(
                name="Concurrent Operations",
                duration=duration,
                success=True,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                throughput=throughput
            )
        except Exception as e:
            return BenchmarkResult(
                name="Concurrent Operations",
                duration=time.time() - start_time,
                success=False,
                memory_usage=0,
                cpu_usage=0,
                throughput=0,
                error_message=str(e)
            )

    async def benchmark_memory_efficiency(self, num_iterations: int = 1000) -> BenchmarkResult:
        """Benchmark memory efficiency."""
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu = self.process.cpu_percent()
        
        try:
            # Create and destroy agents repeatedly
            for i in range(num_iterations):
                agent = SimpleAgent(name=f"memory_test_agent_{i}")
                await agent.execute_task("Simple calculation", {"number": i})
                del agent  # Explicit cleanup
            
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024
            end_cpu = self.process.cpu_percent()
            
            duration = end_time - start_time
            memory_usage = end_memory - start_memory
            cpu_usage = end_cpu - start_cpu
            throughput = num_iterations / duration
            
            return BenchmarkResult(
                name="Memory Efficiency",
                duration=duration,
                success=True,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                throughput=throughput
            )
        except Exception as e:
            return BenchmarkResult(
                name="Memory Efficiency",
                duration=time.time() - start_time,
                success=False,
                memory_usage=0,
                cpu_usage=0,
                throughput=0,
                error_message=str(e)
            )

    async def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmarks."""
        print("🚀 Starting Performance Benchmarks...")
        
        benchmarks = [
            self.benchmark_agent_creation(100),
            self.benchmark_agent_execution(100),
            self.benchmark_tool_execution(100),
            self.benchmark_concurrent_operations(50),
            self.benchmark_memory_efficiency(1000)
        ]
        
        results = []
        for benchmark in benchmarks:
            print(f"Running {benchmark.name}...")
            result = await benchmark
            results.append(result)
            self.results.append(result)
            
            if result.success:
                print(f"✅ {result.name}: {result.throughput:.2f} ops/s, {result.duration:.2f}s, {result.memory_usage:.2f}MB")
            else:
                print(f"❌ {result.name}: Failed - {result.error_message}")
        
        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate performance benchmark report."""
        successful_results = [r for r in self.results if r.success]
        
        if not successful_results:
            return {"error": "No successful benchmarks"}
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_benchmarks": len(self.results),
            "successful_benchmarks": len(successful_results),
            "failed_benchmarks": len(self.results) - len(successful_results),
            "benchmarks": []
        }
        
        for result in successful_results:
            benchmark_data = {
                "name": result.name,
                "duration": result.duration,
                "throughput": result.throughput,
                "memory_usage": result.memory_usage,
                "cpu_usage": result.cpu_usage,
                "success": result.success
            }
            report["benchmarks"].append(benchmark_data)
        
        # Calculate summary statistics
        throughputs = [r.throughput for r in successful_results]
        durations = [r.duration for r in successful_results]
        memory_usages = [r.memory_usage for r in successful_results]
        
        report["summary"] = {
            "avg_throughput": statistics.mean(throughputs),
            "max_throughput": max(throughputs),
            "min_throughput": min(throughputs),
            "avg_duration": statistics.mean(durations),
            "max_duration": max(durations),
            "min_duration": min(durations),
            "total_memory_usage": sum(memory_usages),
            "avg_memory_usage": statistics.mean(memory_usages)
        }
        
        return report

    def save_report(self, filename: str = "benchmark_report.json"):
        """Save benchmark report to file."""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📊 Benchmark report saved to {filename}")

    def create_performance_charts(self):
        """Create performance visualization charts."""
        if not self.results:
            print("No benchmark results to visualize")
            return
        
        successful_results = [r for r in self.results if r.success]
        if not successful_results:
            print("No successful benchmark results to visualize")
            return
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('OpenManus-Youtu Framework Performance Benchmarks', fontsize=16)
        
        names = [r.name for r in successful_results]
        throughputs = [r.throughput for r in successful_results]
        durations = [r.duration for r in successful_results]
        memory_usages = [r.memory_usage for r in successful_results]
        cpu_usages = [r.cpu_usage for r in successful_results]
        
        # Throughput chart
        ax1.bar(names, throughputs, color='skyblue')
        ax1.set_title('Throughput (Operations/Second)')
        ax1.set_ylabel('Ops/s')
        ax1.tick_params(axis='x', rotation=45)
        
        # Duration chart
        ax2.bar(names, durations, color='lightcoral')
        ax2.set_title('Duration (Seconds)')
        ax2.set_ylabel('Seconds')
        ax2.tick_params(axis='x', rotation=45)
        
        # Memory usage chart
        ax3.bar(names, memory_usages, color='lightgreen')
        ax3.set_title('Memory Usage (MB)')
        ax3.set_ylabel('MB')
        ax3.tick_params(axis='x', rotation=45)
        
        # CPU usage chart
        ax4.bar(names, cpu_usages, color='gold')
        ax4.set_title('CPU Usage (%)')
        ax4.set_ylabel('Percentage')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig('performance_benchmarks.png', dpi=300, bbox_inches='tight')
        print("📈 Performance charts saved to performance_benchmarks.png")


async def main():
    """Main benchmark execution."""
    benchmark = PerformanceBenchmark()
    
    # Run all benchmarks
    results = await benchmark.run_all_benchmarks()
    
    # Generate and save report
    benchmark.save_report()
    
    # Create performance charts
    benchmark.create_performance_charts()
    
    # Print summary
    print("\n🎯 Performance Benchmark Summary:")
    print("=" * 50)
    
    for result in results:
        if result.success:
            print(f"{result.name:20} | {result.throughput:8.2f} ops/s | {result.duration:6.2f}s | {result.memory_usage:6.2f}MB")
        else:
            print(f"{result.name:20} | FAILED - {result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())