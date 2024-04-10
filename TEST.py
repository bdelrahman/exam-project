import json
import os
import time
import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk

class QuizApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz App")
        self.master.geometry("1000x900")

        self.style = ttk.Style()  # Create a ttk style object
        self.style.theme_use("clam")  # Set the theme to Adapta

        self.course = self.choose_course()
        self.exam = self.load_exam(self.course)
        self.level = ""
        self.current_question_index = 0
        self.score = 0
        self.x=0
        self.y=0
        self.time_remaining = 300  # 5 minutes for the entire exam
        self.timer_id = None  # To store the timer ID for cancellation

        
        self.create_widgets()
    
    
    def choose_course(self,error="" ):
        
        course = simpledialog.askstring("exam", f"Choose course {error} : Java or Math").capitalize()    
        return course


    def load_exam(self, course):
        while (True):
            file_path = f"{course}.json"
            file_path_correction = os.path.abspath(file_path)
            try:
                file= open(file_path_correction, "r") 
                exam = json.load(file)
                break
            except:
                
                
                course=self.choose_course("file not found oop!!")
        return exam
    def create_widgets(self):
        # Use themed widgets
        self.label_question = ttk.Label(self.master, text="", wraplength=500, justify="left")
        self.label_question.pack(pady=20)

        self.radio_var = tk.StringVar()
        self.radio_var.set("")

        self.radio_buttons = []
        for letter in  ["A", "B", "C", "D"]:
            radio_button = ttk.Radiobutton(self.master, text="", variable=self.radio_var, value=letter)
            radio_button.pack()
            self.radio_buttons.append(radio_button)

        # Use themed buttons
        self.btn_next = ttk.Button(self.master, text="Next", command=self.next_question)
        self.btn_next.pack(side=tk.RIGHT, padx=10)

        self.btn_back = ttk.Button(self.master, text="Back", command=self.previous_question)
        self.btn_back.pack(side=tk.LEFT, padx=10)

        self.label_timer = ttk.Label(self.master, text="Timer: 300 seconds")
        self.label_timer.pack()

        self.show_exam()



    def show_exam(self):
        
        self.level = self.show_exam_dialog()

        if self.level is None:  # If the user cancels the difficulty selection dialog
            self.master.destroy()
            return

        while(True):
            try:
                
                self.exam[self.level] = random.sample(self.exam[self.level], 5)
                
                break
            except:
                self.level = self.show_exam_dialog("please try agian")

      

        

        self.current_question_index = 0
        self.score = 0

        self.show_question()

    def show_exam_dialog(self, error=""):
        level = simpledialog.askstring("Select Difficulty",f"{error} Choose difficulty: easy, medium, or hard")
        return level

    def show_question(self):
        self.label_timer.config(text=f"Timer: {self.time_remaining} seconds")
        self.timer_id = self.master.after(1000, self.update_timer)

        question_data = self.exam[self.level][self.current_question_index]
        self.label_question.config(text=question_data["question"])

        for i, (option, letter) in enumerate(zip(question_data["options"].values(), ["A", "B", "C", "D"])):
            self.radio_buttons[i].config(text=f"{letter}: {option}")

    def next_question(self):
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

        self.process_answer()

        if self.current_question_index < len(self.exam[self.level]) - 1:
            self.current_question_index += 1
            self.show_question()
        else:
            self.show_review()

    def previous_question(self):
        self.y+=1
        self.process_answer()
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

        if self.current_question_index > 0:
            self.current_question_index -= 1
            
            self.show_question()

    def process_answer(self):
        user_answer = self.radio_var.get().upper() if self.radio_var.get() else None
        correct_answer = self.exam[self.level][self.current_question_index]["answer"]
        
        if user_answer is None:
            # No answer selected by the user
            self.x+=1# Deduct points for unanswered questions
        elif user_answer is not None and self.y>0 and  self.x<=-1 :self.x-=1
        elif user_answer == correct_answer:
            self.score += 1
         
    def update_timer(self):
        if self.time_remaining > 0:
            self.label_timer.config(text=f"Timer: {self.time_remaining} seconds")
            self.timer_id = self.master.after(1000, self.update_timer)
            self.time_remaining -= 1
        else:
            self.process_answer()
            self.show_review()

    
    def show_review(self):
        if self.timer_id:
            self.master.after_cancel(self.timer_id)

        self.master.withdraw()  # Hide the main window temporarily

        review_window = tk.Toplevel(self.master)
        review_window.title("Review Answers")
        review_window.geometry("600x400")

        review_text = tk.Text(review_window, wrap="word", height=20, width=80)
        review_text.pack(padx=20, pady=20)

        review_text.insert(tk.END, f"Your final score is {self.score}/{len(self.exam[self.level])}\n\n")
        review_text.insert(tk.END, "Review:\n\n")

        for i, q in enumerate(self.exam[self.level]):
            review_text.insert(tk.END, f"Question {i + 1}:\n")
            review_text.insert(tk.END, f"  {q['question']}\n")

            for option, letter in zip(q["options"].values(), ["A", "B", "C", "D"]):
                review_text.insert(tk.END, f"  {letter}: {option}\n")
            user_answer = self.exam[self.level][i]["options"].get(self.radio_var.get().upper())
            correct_answer = self.exam[self.level][i]["options"][q["answer"]]

            if self.x==0 :
                if user_answer == correct_answer:
                    review_text.insert(tk.END, f"\n  Your answer: {user_answer}\n")
                    review_text.insert(tk.END, f"\n  Correct answer: {correct_answer}\n\n")
                    review_text.tag_configure("Correct", foreground="green")
                    review_text.tag_add("Correct", f"insert - {len(f'\n  Your answer: {user_answer}\n\n  Correct answer: {correct_answer}\n\n')} chars", "insert")
                else:
                    review_text.insert(tk.END, f"\n  Your answer: {user_answer}\n")
                    review_text.insert(tk.END, f"\n  Correct answer: {correct_answer}\n\n")
                    review_text.tag_configure("Incorrect", foreground="red")
                    review_text.tag_add("Incorrect", f"insert - {len(f'\n  Your answer: {user_answer}\n\n  Correct answer: {correct_answer}\n\n')} chars", "insert")
            else:
                review_text.insert(tk.END, f"\n  No answer provided.\n")
                review_text.insert(tk.END, f"\n  Correct answer: {correct_answer}\n\n")
                review_text.tag_configure("NoAnswer", foreground="blue")
                review_text.tag_add("NoAnswer", f"insert - {len(f'\n  No answer provided.\n\n  Correct answer: {correct_answer}\n\n')} chars", "insert")
                self.x-=1  # Deduct points for questions with no answer
                    

        half_degree = len(self.exam[self.level]) / 2

        if self.score >= half_degree:
            review_text.insert(tk.END, f"Congratulations! :3\nYou got {round(self.score/len(self.exam[self.level]),2)*100}%", "congratulations")
            review_text.tag_configure("congratulations", foreground="green")
        else:
            review_text.insert(tk.END, f"Good Luck Next Time! :)\nSadly, You got {round(self.score/len(self.exam[self.level]),2)*100}%", "good_luck")
            review_text.tag_configure("good_luck", foreground="red")

        btn_exit = tk.Button(review_window, text="Exit", command=self.master.destroy)
        btn_exit.pack()
if __name__ == "__main__":
    import random  

    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
