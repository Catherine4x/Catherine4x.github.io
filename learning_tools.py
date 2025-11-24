#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自主学习与时间管理工具集
作者: [你的名字]
创建时间: 2024
"""

import datetime
import json
import os
from typing import List, Dict

class LearningTracker:
    """学习进度跟踪器"""
    
    def __init__(self, data_file="learning_data.json"):
        self.data_file = data_file
        self.load_data()
    
    def load_data(self):
        """加载学习数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                "subjects": {},
                "study_sessions": [],
                "goals": []
            }
    
    def save_data(self):
        """保存学习数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_study_session(self, subject: str, duration: int, topics: List[str]):
        """添加学习记录"""
        session = {
            "date": datetime.datetime.now().isoformat(),
            "subject": subject,
            "duration": duration,  # 分钟
            "topics": topics
        }
        self.data["study_sessions"].append(session)
        self.save_data()
        print(f"✅ 已记录学习: {subject} - {duration}分钟")
    
    def set_learning_goal(self, subject: str, goal: str, deadline: str):
        """设置学习目标"""
        goal_data = {
            "subject": subject,
            "goal": goal,
            "deadline": deadline,
            "created": datetime.datetime.now().isoformat(),
            "completed": False
        }
        self.data["goals"].append(goal_data)
        self.save_data()
        print(f"🎯 已设定目标: {subject} - {goal}")

class TimeManager:
    """时间管理工具"""
    
    @staticmethod
    def pomodoro_timer(work_minutes=25, break_minutes=5, cycles=4):
        """番茄工作法计时器"""
        print("🍅 番茄工作法开始！")
        for cycle in range(cycles):
            print(f"\n=== 第 {cycle + 1} 个番茄钟 ===")
            print(f"专注工作时间: {work_minutes} 分钟")
            # 这里实际使用时需要真正的计时功能
            input("按回车开始专注...")
            print("⏰ 时间到！休息一下")
            
            if cycle < cycles - 1:  # 不是最后一个周期
                print(f"休息时间: {break_minutes} 分钟")
                input("按回车继续下一个番茄钟...")
        
        print("\n🎉 完成所有番茄钟！建议长时间休息15-30分钟")
    
    @staticmethod
    def time_block_scheduler():
        """时间块规划器"""
        time_blocks = {
            "06:00-08:00": "早晨学习块 - 记忆性内容",
            "09:00-11:30": "上午深度块 - 难点攻克", 
            "14:00-17:00": "下午实践块 - 练习应用",
            "19:00-21:00": "晚上复习块 - 总结归纳",
            "21:00-22:00": "自由安排块 - 阅读放松"
        }
        
        print("⏰ 推荐时间块安排:")
        for time, activity in time_blocks.items():
            print(f"  {time}: {activity}")
        
        return time_blocks

class StudyMethods:
    """学习方法库"""
    
    @staticmethod
    def feynman_technique(topic: str):
        """费曼学习法"""
        print("\n🎓 使用费曼学习法:")
        print("1. 选择要学习的概念")
        print(f"   概念: {topic}")
        print("2. 向不懂的人解释这个概念")
        print("3. 发现理解漏洞，回顾学习")
        print("4. 简化语言，使用类比")
    
    @staticmethod
    def active_recall_method():
        """主动回忆法"""
        print("\n💡 主动回忆法步骤:")
        steps = [
            "学习一段内容后合上材料",
            "尝试回忆关键概念和细节", 
            "检查回忆的准确性",
            "重点复习遗忘或错误的部分"
        ]
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")

def main():
    """主函数 - 提供交互式菜单"""
    tracker = LearningTracker()
    time_manager = TimeManager()
    study_methods = StudyMethods()
    
    while True:
        print("\n" + "="*50)
        print("📚 自主学习与时间管理系统")
        print("="*50)
        print("1. 记录学习进度")
        print("2. 设定学习目标") 
        print("3. 番茄工作法")
        print("4. 查看时间块安排")
        print("5. 学习方法指导")
        print("6. 退出系统")
        print("-"*50)
        
        choice = input("请选择功能 (1-6): ").strip()
        
        if choice == "1":
            subject = input("学习科目: ")
            duration = int(input("学习时长(分钟): "))
            topics = input("学习主题(用逗号分隔): ").split(",")
            tracker.add_study_session(subject, duration, topics)
            
        elif choice == "2":
            subject = input("目标科目: ")
            goal = input("具体目标: ")
            deadline = input("截止日期(YYYY-MM-DD): ")
            tracker.set_learning_goal(subject, goal, deadline)
            
        elif choice == "3":
            time_manager.pomodoro_timer()
            
        elif choice == "4":
            time_manager.time_block_scheduler()
            
        elif choice == "5":
            print("\n选择学习方法:")
            print("1. 费曼学习法")
            print("2. 主动回忆法")
            method_choice = input("请选择 (1-2): ")
            
            if method_choice == "1":
                topic = input("输入要学习的概念: ")
                study_methods.feynman_technique(topic)
            elif method_choice == "2":
                study_methods.active_recall_method()
                
        elif choice == "6":
            print("👋 感谢使用！保持学习，天天进步！")
            break
            
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()
