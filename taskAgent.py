import os
from datetime import datetime, timedelta
import json
from openai import OpenAI
from dotenv import load_dotenv

class AITaskAgent:
    def __init__(self, api_key):
        self.tasks = self.load_tasks()
        self.task_history = []
        self.client = OpenAI(api_key=api_key)

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_tasks(self):
        with open('tasks.json', 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def analyze_task_description(self, description):
        """Use AI to analyze the task and suggest priority, deadline, and categorization"""
        prompt = f"""Analyze this task: "{description}"
        Provide a JSON response with:
        1. Suggested priority (high/medium/low)
        2. Estimated time to complete (in hours)
        3. Category (e.g., development, writing, research)
        4. Any potential subtasks
        Base this on the task description and common project management practices."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.choices[0].message.content)

    def add_task(self, description):
        # Use AI to analyze the task
        analysis = self.analyze_task_description(description)
        print("analysis: ")
        print(analysis)
        task = {
            'id': len(self.tasks) + 1,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'priority': analysis['priority'],
            'estimated_hours': analysis['estimated_time'],
            'category': analysis['category'],
            'subtasks': analysis['potential_subtasks'],
            'status': 'pending'
        }
        self.tasks.append(task)
        self.save_tasks()
        return f"Added task with AI analysis: {task}"

    def get_smart_recommendations(self):
        """Use AI to provide intelligent task recommendations"""
        if not self.tasks:
            return "No tasks available for analysis"

        # Create a context of all current tasks
        tasks_context = "\n".join([
            f"Task {t['id']}: {t['description']} (Priority: {t['priority']}, Status: {t['status']})"
            for t in self.tasks
        ])

        prompt = f"""Given these tasks:
        {tasks_context}
        
        Provide recommendations for:
        1. Which task should be done next and why
        2. Any tasks that might be related or could be combined
        3. Suggestions for optimal task scheduling
        Consider priorities, deadlines, and task relationships in your analysis."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

    def generate_progress_report(self):
        """Use AI to generate a natural language progress report"""
        completed = [t for t in self.tasks if t['status'] == 'completed']
        pending = [t for t in self.tasks if t['status'] == 'pending']

        context = f"""
        Completed Tasks: {len(completed)}
        Pending Tasks: {len(pending)}
        Task Details: {json.dumps(self.tasks, indent=2)}
        """

        prompt = f"""Based on this task data:
        {context}
        
        Generate a concise progress report that includes:
        1. Overall progress summary
        2. Key achievements
        3. Areas needing attention
        4. Suggestions for improving productivity
        Use a professional but engaging tone."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

    def display_tasks(self):
            if not self.tasks:
                return "No tasks found."
            
            task_list = []
            for task in self.tasks:
                status = "✓" if task['status'] == 'completed' else "□"
                task_list.append(f"{status} Task {task['id']}: {task['description']} "
                            f"(Priority: {task['priority']}, Category: {task['category']})")
            return "\n".join(task_list)

    def complete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                self.task_history.append({
                    'action': 'complete',
                    'task_id': task_id,
                    'timestamp': datetime.now().isoformat()
                })
                self.save_tasks()
                return f"Completed task: {task['description']}"
        return "Task not found"


def display_menu():
    print("\n=== AI Task Manager ===")
    print("1. Add new task")
    print("2. View all tasks")
    print("3. Get AI recommendations")
    print("4. Generate progress report")
    print("5. Mark task as complete")
    print("6. Exit")
    return input("Choose an option (1-6): ")

def main():

    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        raise ValueError("No API key found!!")

    # Initialize agent with your OpenAI API key
    agent = AITaskAgent(api_key=api_key)
    
    # Example usage
    while True:
        choice = display_menu()
        
        try:
            if choice == '1':
                task_description = input("\nEnter task description: ")
                result = agent.add_task(task_description)
                print("\nTask added with AI analysis:")
                print(result)

            elif choice == '2':
                print("\nCurrent Tasks:")
                print(agent.display_tasks())

            elif choice == '3':
                print("\nGetting AI Recommendations...")
                recommendations = agent.get_smart_recommendations()
                print(recommendations)

            elif choice == '4':
                print("\nGenerating Progress Report...")
                report = agent.generate_progress_report()
                print(report)

            elif choice == '5':
                print("\nCurrent Tasks:")
                print(agent.display_tasks())
                task_id = input("Enter task ID to mark as complete: ")
                if task_id.isdigit():
                    result = agent.complete_task(int(task_id))
                    print(result)
                else:
                    print("Please enter a valid task ID")

            elif choice == '6':
                print("Thank you for using AI Task Manager!")
                break

            else:
                print("Invalid choice. Please try again.")

            input("\nPress Enter to continue...")

        except Exception as e:
            print(f"An error occurred: {e}")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()