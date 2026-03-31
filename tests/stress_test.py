"""
APISTD 稳定性压力测试脚本

持续向目标服务器发送请求，测试 APISTD 的稳定性、性能和可靠性
"""

import requests
import time
import statistics
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import sys


class StabilityTester:
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.stats = defaultdict(list)
        self.errors = defaultdict(int)
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.start_time = None
        
    def make_request(self, endpoint, method='GET', data=None):
        """发送单个请求并记录结果"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=self.timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=self.timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=self.timeout)
            elif method == 'DELETE':
                response = requests.delete(url, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            duration = (time.time() - start_time) * 1000  # 转换为毫秒
            
            self.total_requests += 1
            if response.status_code < 400:
                self.successful_requests += 1
                status = 'success'
            else:
                self.failed_requests += 1
                status = f'http_{response.status_code}'
                self.errors[f'HTTP {response.status_code}'] += 1
            
            self.stats[endpoint].append(duration)
            
            return {
                'endpoint': endpoint,
                'status': status,
                'status_code': response.status_code,
                'duration_ms': duration,
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.Timeout:
            duration = (time.time() - start_time) * 1000
            self.total_requests += 1
            self.failed_requests += 1
            self.errors['Timeout'] += 1
            self.stats[endpoint].append(duration)
            
            return {
                'endpoint': endpoint,
                'status': 'timeout',
                'status_code': None,
                'duration_ms': duration,
                'timestamp': datetime.now().isoformat(),
                'error': 'Request timeout'
            }
            
        except requests.exceptions.ConnectionError as e:
            duration = (time.time() - start_time) * 1000
            self.total_requests += 1
            self.failed_requests += 1
            self.errors['Connection Error'] += 1
            self.stats[endpoint].append(duration)
            
            return {
                'endpoint': endpoint,
                'status': 'connection_error',
                'status_code': None,
                'duration_ms': duration,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.total_requests += 1
            self.failed_requests += 1
            self.errors[type(e).__name__] += 1
            self.stats[endpoint].append(duration)
            
            return {
                'endpoint': endpoint,
                'status': 'error',
                'status_code': None,
                'duration_ms': duration,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def run_sequential_test(self, endpoints, iterations=1000, delay=0):
        """顺序执行测试"""
        print(f"\n开始顺序压力测试")
        print(f"目标：{self.base_url}")
        print(f"端点：{len(endpoints)} 个")
        print(f"迭代次数：{iterations}")
        print(f"总请求数：{len(endpoints) * iterations}")
        print("-" * 80)
        
        self.start_time = datetime.now()
        
        for i in range(iterations):
            for endpoint in endpoints:
                result = self.make_request(endpoint)
                
                # 每 100 次请求打印一次进度
                if self.total_requests % 100 == 0:
                    success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
                    print(f"[{self.total_requests}] 成功：{self.successful_requests} | "
                          f"失败：{self.failed_requests} | "
                          f"成功率：{success_rate:.2f}%")
                
                if delay > 0:
                    time.sleep(delay)
        
        self.print_report()
    
    def run_concurrent_test(self, endpoints, iterations=1000, workers=10):
        """并发执行测试"""
        print(f"\n开始并发压力测试")
        print(f"目标：{self.base_url}")
        print(f"端点：{len(endpoints)} 个")
        print(f"迭代次数：{iterations}")
        print(f"并发数：{workers}")
        print(f"总请求数：{len(endpoints) * iterations}")
        print("-" * 80)
        
        self.start_time = datetime.now()
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for i in range(iterations):
                for endpoint in endpoints:
                    futures.append(executor.submit(self.make_request, endpoint))
            
            # 处理结果
            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                
                # 每 100 次请求打印一次进度
                if (i + 1) % 100 == 0:
                    success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0
                    print(f"[{self.total_requests}] 成功：{self.successful_requests} | "
                          f"失败：{self.failed_requests} | "
                          f"成功率：{success_rate:.2f}%")
        
        self.print_report()
    
    def print_report(self):
        """打印测试报告"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("APISTD 稳定性测试报告")
        print("=" * 80)
        print(f"测试时间：{self.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时：{duration}")
        print(f"目标地址：{self.base_url}")
        print()
        
        # 总体统计
        print("📊 总体统计")
        print("-" * 80)
        print(f"总请求数：{self.total_requests}")
        print(f"成功请求：{self.successful_requests}")
        print(f"失败请求：{self.failed_requests}")
        
        if self.total_requests > 0:
            success_rate = self.successful_requests / self.total_requests * 100
            print(f"成功率：{success_rate:.2f}%")
            rps = self.total_requests / duration.total_seconds()
            print(f"请求/秒 (RPS): {rps:.2f}")
        
        # 错误统计
        if self.errors:
            print("\n❌ 错误统计")
            print("-" * 80)
            for error_type, count in sorted(self.errors.items(), key=lambda x: x[1], reverse=True):
                percentage = count / self.total_requests * 100 if self.total_requests > 0 else 0
                print(f"{error_type}: {count} ({percentage:.2f}%)")
        
        # 性能统计
        print("\n⚡ 性能统计 (毫秒)")
        print("-" * 80)
        
        all_durations = []
        for endpoint_list in self.stats.values():
            all_durations.extend(endpoint_list)
        
        if all_durations:
            print(f"平均响应时间：{statistics.mean(all_durations):.2f} ms")
            print(f"中位数：{statistics.median(all_durations):.2f} ms")
            print(f"P95: {sorted(all_durations)[int(len(all_durations) * 0.95)]:.2f} ms")
            print(f"P99: {sorted(all_durations)[int(len(all_durations) * 0.99)]:.2f} ms")
            print(f"最小：{min(all_durations):.2f} ms")
            print(f"最大：{max(all_durations):.2f} ms")
        
        # 按端点统计
        print("\n📍 端点性能详情")
        print("-" * 80)
        for endpoint, durations in self.stats.items():
            if durations:
                avg = statistics.mean(durations)
                p95 = sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0]
                print(f"{endpoint:30s} 平均：{avg:8.2f}ms  P95: {p95:8.2f}ms  请求数：{len(durations)}")
        
        print("\n" + "=" * 80)
        
        # 稳定性评估
        print("\n🎯 稳定性评估")
        print("-" * 80)
        if success_rate >= 99.9:
            print("✅ 优秀 - 系统非常稳定")
        elif success_rate >= 99:
            print("✅ 良好 - 系统稳定")
        elif success_rate >= 95:
            print("⚠️  一般 - 有少量错误")
        else:
            print("❌ 需改进 - 错误率较高")
        
        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description='APISTD 稳定性压力测试')
    parser.add_argument('--base-url', default='http://192.168.1.5:5000',
                        help='目标服务器地址 (默认：http://192.168.1.5:5000)')
    parser.add_argument('--iterations', type=int, default=1000,
                        help='迭代次数 (默认：1000)')
    parser.add_argument('--workers', type=int, default=10,
                        help='并发工作线程数 (默认：10)')
    parser.add_argument('--mode', choices=['sequential', 'concurrent'], default='concurrent',
                        help='测试模式：sequential (顺序) 或 concurrent (并发)')
    parser.add_argument('--delay', type=float, default=0,
                        help='请求间隔时间 (秒，默认：0)')
    
    args = parser.parse_args()
    
    # 定义测试端点
    endpoints = [
        '/users/5',
        '/users',
        '/users/1',
        '/users/2',
        '/users/3',
        '/users/4',
        '/users/5',
        # 可以添加更多端点
        # '/health',
        # '/status',
        # '/api/data',
    ]
    
    tester = StabilityTester(args.base_url)
    
    if args.mode == 'sequential':
        tester.run_sequential_test(endpoints, args.iterations, args.delay)
    else:
        tester.run_concurrent_test(endpoints, args.iterations, args.workers)


if __name__ == '__main__':
    main()
