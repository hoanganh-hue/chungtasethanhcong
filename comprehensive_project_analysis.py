#!/usr/bin/env python3
"""
Comprehensive Project Analysis Script
Scans and analyzes the entire project to assess completion status
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import ast

# Project root directory
PROJECT_ROOT = Path("/home/runner/work/chungtasethanhcong/chungtasethanhcong")


def count_lines_in_file(file_path: Path) -> Tuple[int, int, int]:
    """Count total, code, and comment lines in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            total_lines = len(lines)
            
            # Count code and comment lines
            code_lines = 0
            comment_lines = 0
            blank_lines = 0
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    blank_lines += 1
                elif stripped.startswith('#'):
                    comment_lines += 1
                else:
                    code_lines += 1
            
            return total_lines, code_lines, comment_lines
    except Exception as e:
        return 0, 0, 0


def analyze_python_file(file_path: Path) -> Dict:
    """Analyze a Python file for classes, functions, etc."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=str(file_path))
            
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_'):
                        functions.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.unparse(node))
            
            return {
                "classes": len(classes),
                "functions": len(functions),
                "imports": len(imports),
                "class_names": classes[:10],  # First 10 classes
                "function_names": functions[:10]  # First 10 functions
            }
    except Exception as e:
        return {"error": str(e)}


def scan_directory(directory: Path, extensions: List[str]) -> Dict:
    """Scan a directory for files with specific extensions"""
    files = []
    total_lines = 0
    code_lines = 0
    comment_lines = 0
    
    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            if '.git' not in str(file_path) and '__pycache__' not in str(file_path):
                rel_path = file_path.relative_to(PROJECT_ROOT)
                t, c, com = count_lines_in_file(file_path)
                
                file_info = {
                    "path": str(rel_path),
                    "size": file_path.stat().st_size,
                    "total_lines": t,
                    "code_lines": c,
                    "comment_lines": com
                }
                
                # Add Python-specific analysis
                if ext == '.py':
                    file_info["analysis"] = analyze_python_file(file_path)
                
                files.append(file_info)
                total_lines += t
                code_lines += c
                comment_lines += com
    
    return {
        "count": len(files),
        "total_lines": total_lines,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "files": files
    }


def analyze_project_structure() -> Dict:
    """Analyze the complete project structure"""
    
    print("🔍 Scanning project structure...")
    
    # Scan different file types
    python_files = scan_directory(PROJECT_ROOT / "src", ['.py'])
    test_files = scan_directory(PROJECT_ROOT / "tests", ['.py']) if (PROJECT_ROOT / "tests").exists() else {"count": 0, "files": []}
    script_files = scan_directory(PROJECT_ROOT / "scripts", ['.py']) if (PROJECT_ROOT / "scripts").exists() else {"count": 0, "files": []}
    example_files = scan_directory(PROJECT_ROOT / "examples", ['.py']) if (PROJECT_ROOT / "examples").exists() else {"count": 0, "files": []}
    
    # Scan documentation
    doc_files = scan_directory(PROJECT_ROOT, ['.md'])
    config_files = scan_directory(PROJECT_ROOT, ['.yaml', '.yml', '.json', '.toml'])
    
    # Analyze directory structure
    directories = {}
    for item in (PROJECT_ROOT / "src").rglob("*"):
        if item.is_dir() and '.git' not in str(item) and '__pycache__' not in str(item):
            rel_path = item.relative_to(PROJECT_ROOT)
            py_files = list(item.glob("*.py"))
            directories[str(rel_path)] = {
                "python_files": len(py_files),
                "has_init": (item / "__init__.py").exists()
            }
    
    return {
        "python_files": python_files,
        "test_files": test_files,
        "script_files": script_files,
        "example_files": example_files,
        "documentation": doc_files,
        "config_files": config_files,
        "directories": directories
    }


def calculate_completion_metrics(analysis: Dict) -> Dict:
    """Calculate completion metrics based on analysis"""
    
    # Define expected components and their weights
    components = {
        "Core Framework": {
            "weight": 25,
            "expected_files": ["unified_agent.py", "config.py", "tool_registry.py", "environment.py", "memory.py", "state_manager.py"],
            "directory": "src/core"
        },
        "Agents": {
            "weight": 20,
            "expected_files": ["simple_agent.py", "browser_agent.py", "orchestra_agent.py", "meta_agent.py"],
            "directory": "src/agents"
        },
        "Tools": {
            "weight": 15,
            "expected_files": ["web_tools.py", "file_tools.py", "data_tools.py", "email_tools.py"],
            "directory": "src/tools"
        },
        "API": {
            "weight": 15,
            "expected_files": ["server.py", "routes.py", "models.py"],
            "directory": "src/api"
        },
        "Security": {
            "weight": 10,
            "expected_files": ["authentication.py", "rate_limiting.py"],
            "directory": "src/security"
        },
        "Testing": {
            "weight": 10,
            "expected_files": [],
            "directory": "tests"
        },
        "Documentation": {
            "weight": 5,
            "expected_files": ["README.md", "architecture.md", "USER_GUIDE.md"],
            "directory": "docs"
        }
    }
    
    # Check completion for each component
    completion_details = {}
    total_score = 0
    
    for component_name, component_info in components.items():
        directory = PROJECT_ROOT / component_info["directory"]
        expected_files = component_info["expected_files"]
        weight = component_info["weight"]
        
        if directory.exists():
            existing_files = [f.name for f in directory.rglob("*.py")] if component_name != "Documentation" else [f.name for f in directory.rglob("*.md")]
            
            if expected_files:
                found_files = [f for f in expected_files if any(f in ef for ef in existing_files)]
                completion_rate = (len(found_files) / len(expected_files)) * 100
            else:
                # For directories without specific files, check if any files exist
                completion_rate = 100 if existing_files else 0
            
            all_files_in_dir = list(directory.rglob("*.py" if component_name != "Documentation" else "*.md"))
            
            completion_details[component_name] = {
                "completion_rate": completion_rate,
                "weight": weight,
                "weighted_score": (completion_rate * weight) / 100,
                "expected_files": len(expected_files),
                "found_files": len([f for f in expected_files if any(f in ef for ef in existing_files)]) if expected_files else len(all_files_in_dir),
                "total_files": len(all_files_in_dir),
                "status": "✅ Complete" if completion_rate >= 90 else "🔄 In Progress" if completion_rate >= 50 else "❌ Incomplete"
            }
            
            total_score += completion_details[component_name]["weighted_score"]
        else:
            completion_details[component_name] = {
                "completion_rate": 0,
                "weight": weight,
                "weighted_score": 0,
                "expected_files": len(expected_files),
                "found_files": 0,
                "total_files": 0,
                "status": "❌ Not Started"
            }
    
    return {
        "overall_completion": total_score,
        "components": completion_details
    }


def generate_report(analysis: Dict, metrics: Dict) -> str:
    """Generate a comprehensive report"""
    
    report = []
    report.append("=" * 80)
    report.append("📊 BÁO CÁO PHÂN TÍCH DỰ ÁN TOÀN DIỆN")
    report.append("OpenManus-Youtu Integrated Framework")
    report.append("=" * 80)
    report.append("")
    
    # Overview
    report.append("🎯 TỔNG QUAN DỰ ÁN")
    report.append("-" * 80)
    report.append(f"📅 Ngày phân tích: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"📂 Thư mục gốc: {PROJECT_ROOT}")
    report.append("")
    
    # File Statistics
    report.append("📈 THỐNG KÊ FILE")
    report.append("-" * 80)
    report.append(f"Python Files (src):     {analysis['python_files']['count']:4d} files | {analysis['python_files']['total_lines']:6d} lines | {analysis['python_files']['code_lines']:6d} code | {analysis['python_files']['comment_lines']:6d} comments")
    report.append(f"Test Files:             {analysis['test_files']['count']:4d} files | {analysis['test_files'].get('total_lines', 0):6d} lines")
    report.append(f"Script Files:           {analysis['script_files']['count']:4d} files | {analysis['script_files'].get('total_lines', 0):6d} lines")
    report.append(f"Example Files:          {analysis['example_files']['count']:4d} files | {analysis['example_files'].get('total_lines', 0):6d} lines")
    report.append(f"Documentation:          {analysis['documentation']['count']:4d} files | {analysis['documentation']['total_lines']:6d} lines")
    report.append(f"Config Files:           {analysis['config_files']['count']:4d} files")
    report.append("")
    
    total_py_files = (analysis['python_files']['count'] + 
                      analysis['test_files']['count'] + 
                      analysis['script_files']['count'] + 
                      analysis['example_files']['count'])
    total_lines = (analysis['python_files']['total_lines'] + 
                   analysis['test_files'].get('total_lines', 0) + 
                   analysis['script_files'].get('total_lines', 0) + 
                   analysis['example_files'].get('total_lines', 0))
    
    report.append(f"📊 TỔNG CỘNG:           {total_py_files:4d} Python files | {total_lines:6d} total lines")
    report.append("")
    
    # Completion Metrics
    report.append("🎯 TỶ LỆ HOÀN THÀNH")
    report.append("-" * 80)
    report.append(f"Overall Completion: {metrics['overall_completion']:.1f}%")
    report.append("")
    
    # Component Details
    report.append("📋 CHI TIẾT CÁC THÀNH PHẦN")
    report.append("-" * 80)
    for component_name, details in metrics['components'].items():
        report.append(f"\n{component_name} (Trọng số: {details['weight']}%)")
        report.append(f"  Status: {details['status']}")
        report.append(f"  Completion: {details['completion_rate']:.1f}%")
        report.append(f"  Files: {details['found_files']}/{details['expected_files']} expected, {details['total_files']} total")
        report.append(f"  Weighted Score: {details['weighted_score']:.2f}")
    report.append("")
    
    # Directory Structure
    report.append("📁 CẤU TRÚC THƯ MỤC")
    report.append("-" * 80)
    for dir_path, dir_info in sorted(analysis['directories'].items()):
        init_marker = "✅" if dir_info['has_init'] else "❌"
        report.append(f"{init_marker} {dir_path:40s} - {dir_info['python_files']} files")
    report.append("")
    
    # Code Quality Metrics
    report.append("💎 CHẤT LƯỢNG CODE")
    report.append("-" * 80)
    
    # Calculate metrics
    total_classes = 0
    total_functions = 0
    files_with_docstrings = 0
    
    for file_info in analysis['python_files']['files']:
        if 'analysis' in file_info and 'error' not in file_info['analysis']:
            total_classes += file_info['analysis']['classes']
            total_functions += file_info['analysis']['functions']
    
    avg_lines_per_file = analysis['python_files']['total_lines'] / max(analysis['python_files']['count'], 1)
    code_to_comment_ratio = analysis['python_files']['code_lines'] / max(analysis['python_files']['comment_lines'], 1)
    
    report.append(f"Total Classes:          {total_classes}")
    report.append(f"Total Functions:        {total_functions}")
    report.append(f"Avg Lines per File:     {avg_lines_per_file:.1f}")
    report.append(f"Code/Comment Ratio:     {code_to_comment_ratio:.2f}")
    report.append("")
    
    # Top 10 largest files
    report.append("📄 10 FILE LỚN NHẤT")
    report.append("-" * 80)
    sorted_files = sorted(analysis['python_files']['files'], key=lambda x: x['total_lines'], reverse=True)[:10]
    for i, file_info in enumerate(sorted_files, 1):
        report.append(f"{i:2d}. {file_info['path']:50s} - {file_info['total_lines']:5d} lines")
    report.append("")
    
    # Summary
    report.append("🎉 KẾT LUẬN")
    report.append("-" * 80)
    
    if metrics['overall_completion'] >= 90:
        report.append("✅ Dự án đã hoàn thành gần như toàn bộ!")
        report.append("   Tất cả các thành phần chính đã được triển khai.")
    elif metrics['overall_completion'] >= 70:
        report.append("🔄 Dự án đã hoàn thành phần lớn!")
        report.append("   Một số thành phần còn cần hoàn thiện.")
    elif metrics['overall_completion'] >= 50:
        report.append("🔄 Dự án đang trong quá trình phát triển.")
        report.append("   Nhiều thành phần đã hoàn thành nhưng vẫn còn công việc.")
    else:
        report.append("❌ Dự án còn nhiều công việc cần thực hiện.")
        report.append("   Cần tập trung hoàn thiện các thành phần chính.")
    
    report.append("")
    report.append("📊 Đánh giá chuyên nghiệp:")
    report.append(f"   - Tỷ lệ hoàn thành tổng thể: {metrics['overall_completion']:.1f}%")
    report.append(f"   - Tổng số file Python: {total_py_files} files")
    report.append(f"   - Tổng số dòng code: {total_lines:,} lines")
    report.append(f"   - Số lượng thành phần hoàn thành: {sum(1 for c in metrics['components'].values() if c['completion_rate'] >= 90)}/{len(metrics['components'])}")
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)


def save_results(analysis: Dict, metrics: Dict, report: str):
    """Save analysis results to files"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON data
    json_output = {
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis,
        "metrics": metrics
    }
    
    json_file = PROJECT_ROOT / f"project_analysis_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    
    # Save text report
    report_file = PROJECT_ROOT / f"PROJECT_ANALYSIS_REPORT_{timestamp}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Also save as latest
    latest_report = PROJECT_ROOT / "PROJECT_ANALYSIS_REPORT_LATEST.md"
    with open(latest_report, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Results saved to:")
    print(f"   - {json_file}")
    print(f"   - {report_file}")
    print(f"   - {latest_report}")


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("🚀 Starting Comprehensive Project Analysis")
    print("=" * 80 + "\n")
    
    # Analyze project
    analysis = analyze_project_structure()
    
    # Calculate metrics
    metrics = calculate_completion_metrics(analysis)
    
    # Generate report
    report = generate_report(analysis, metrics)
    
    # Print report
    print(report)
    
    # Save results
    save_results(analysis, metrics, report)
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
