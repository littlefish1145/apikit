"""
APISTD 快速稳定性测试脚本

针对单个端点进行快速压力测试
"""

import requests
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import statistics


def quick_stress_test(url, iterations=1000, workers=10, timeout=5):
    """
    快速压力测试
    
    Args:
        url: 目标 URL
        iterations: 请求次数
        workers: 并发数
        timeout: 超时时间（秒）
    """
    print(f"\n{'='*70}")
    print(f"APISTD 快速稳定性测试")
    print(f"{'='*70}")
    print(f"目标 URL: {url}")
    print(f"请求次数：{iterations}")
    print(f"并发数：{workers}")
    print(f"超时时间：{timeout}秒")
    print(f"{'='*70}\n")
    
    results = []
    success = 0
    failed = 0
    errors = {}
    start_time = datetime.now()
    
    def make_request():
        nonlocal success, failed
        try:
            r = requests.get(url, timeout=timeout)
            duration = r.elapsed.total_seconds() * 1000
            
            if r.status_code < 400:
                success += 1
                status = 'success'
            else:
                failed += 1
                status = f'http_{r.status_code}'
                errors[f'HTTP {r.status_code}'] = errors.get(f'HTTP {r.status_code}', 0) + 1
            
            return {'status': status, 'duration': duration, 'code': r.status_code}
            
        except requests.Timeout:
            failed += 1
            errors['Timeout'] = errors.get('Timeout', 0) + 1
            return {'status': 'timeout', 'duration': timeout * 1000, 'code': None}
        except Exception as e:
            failed += 1
            errors[type(e).__name__] = errors.get(type(e).__name__, 0) + 1
            return {'status': 'error', 'duration': 0, 'code': None}
    
    # 执行测试
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(lambda _: make_request(), range(iterations)))
    
    # 计算统计
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    durations = [r['duration'] for r in results if r['duration'] > 0]
    
    # 打印报告
    print(f"\n{'='*70}")
    print(f"测试结果报告")
    print(f"{'='*70}")
    print(f"测试时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总耗时：{duration:.2f}秒")
    print(f"\n📊 总体统计")
    print(f"-" * 70)
    print(f"总请求数：{iterations}")
    print(f"成功：{success} ({success/iterations*100:.2f}%)")
    print(f"失败：{failed} ({failed/iterations*100:.2f}%)")
    print(f"RPS: {iterations/duration:.2f}")
    
    if errors:
        print(f"\n❌ 错误统计")
        print(f"-" * 70)
        for error, count in sorted(errors.items(), key=lambda x: x[1], reverse=True):
            print(f"{error}: {count} ({count/iterations*100:.2f}%)")
    
    if durations:
        print(f"\n⚡ 性能统计")
        print(f"-" * 70)
        print(f"平均：{statistics.mean(durations):.2f} ms")
        print(f"中位数：{statistics.median(durations):.2f} ms")
        p95_idx = int(len(durations) * 0.95)
        p99_idx = int(len(durations) * 0.99)
        sorted_durations = sorted(durations)
        print(f"P95: {sorted_durations[p95_idx]:.2f} ms")
        print(f"P99: {sorted_durations[p99_idx]:.2f} ms")
        print(f"最小：{min(durations):.2f} ms")
        print(f"最大：{max(durations):.2f} ms")
    
    # 稳定性评级
    success_rate = success / iterations * 100
    print(f"\n🎯 稳定性评估")
    print(f"-" * 70)
    if success_rate >= 99.9:
        print("✅ 优秀 - 系统非常稳定")
    elif success_rate >= 99:
        print("✅ 良好 - 系统稳定")
    elif success_rate >= 95:
        print("⚠️  一般 - 有少量错误")
    else:
        print("❌ 需改进 - 错误率较高")
    
    print(f"{'='*70}\n")
    
    return success_rate


if __name__ == '__main__':
    # 测试主端点
    url = "http://192.168.1.5:5000/users/5"
    quick_stress_test(url, iterations=1000, workers=10)
    
    # 如果有 404 错误，尝试其他可能的端点
    print("\n提示：如果遇到 404 错误，请检查:")
    print("1. Flask 应用是否正在运行")
    print("2. 路由是否正确配置")
    print("3. 端点路径是否正确")
    print("\n示例端点:")
    print("  - http://192.168.1.5:5000/users/5")
    print("  - http://192.168.1.5:5000/users")
    print("  - http://192.168.1.5:5000/health")
