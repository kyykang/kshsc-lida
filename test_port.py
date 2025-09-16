#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端口连通性测试工具
用于检查指定IP地址和端口是否可以连接
"""

import socket
import sys
from datetime import datetime

def test_port_connection(host, port, timeout=10):
    """
    测试指定主机和端口的连通性
    
    参数:
        host (str): 目标主机IP地址
        port (int): 目标端口号
        timeout (int): 连接超时时间（秒）
    
    返回:
        bool: 连接成功返回True，失败返回False
    """
    try:
        # 创建socket对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置超时时间
        sock.settimeout(timeout)
        
        print(f"正在测试连接到 {host}:{port}...")
        start_time = datetime.now()
        
        # 尝试连接
        result = sock.connect_ex((host, port))
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() * 1000  # 转换为毫秒
        
        # 关闭socket
        sock.close()
        
        if result == 0:
            print(f"✅ 连接成功！耗时: {duration:.2f}ms")
            return True
        else:
            print(f"❌ 连接失败！错误代码: {result}")
            return False
            
    except socket.timeout:
        print(f"❌ 连接超时！（超过{timeout}秒）")
        return False
    except socket.gaierror as e:
        print(f"❌ DNS解析失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 连接异常: {e}")
        return False

def main():
    """
    主函数：测试指定的IP和端口
    """
    host = "10.254.28.17"
    port = 30000
    
    print("=" * 50)
    print("端口连通性测试工具")
    print("=" * 50)
    print(f"目标主机: {host}")
    print(f"目标端口: {port}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 执行连接测试
    success = test_port_connection(host, port)
    
    print("-" * 50)
    if success:
        print("🎉 端口可以正常访问！")
        sys.exit(0)
    else:
        print("⚠️  端口无法访问，可能的原因：")
        print("   1. 目标主机不在线或网络不通")
        print("   2. 目标端口未开放或服务未启动")
        print("   3. 防火墙阻止了连接")
        print("   4. 网络路由问题")
        sys.exit(1)

if __name__ == "__main__":
    main()