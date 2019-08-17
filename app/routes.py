from flask import render_template, flash, redirect, request
from app import application
from app.forms import CppForm
import subprocess
import json
from threading import Timer
import time

kill = lambda process: process.kill()


@application.route("/", methods=["GET", "POST"])
def home():
    form = CppForm()
    if request.method == "POST":
        f = open("compiled/tempCode.cpp", "w+")
        f.write(form.code.data)
        f.close()
        f = open("compiled/tempInput", "w+")
        f.write(form.inputText.data)
        f.close()
        error = ""
        output = ""
        executionTime = 0
        try:
            error = str(
                subprocess.check_output(
                    "g++ compiled/tempCode.cpp -o compiled/tempCode; exit 0",
                    stderr=subprocess.STDOUT,
                    shell=True,
                ),
                "utf-8",
            ).split("\n")

            if error == [""]:
                error = ""

            timeStarted = time.time()
            child = subprocess.Popen(
                ["./compiled/tempCode"],
                stdin=open("compiled/tempInput", "r"),
                stdout=open("compiled/tempOutput", "w"),
                stderr=subprocess.PIPE,
            )
            data = child.communicate(timeout=1)[0]
            executionTime = time.time() - timeStarted
            
            code = child.returncode
            if code==0:
                f = open("compiled/tempOutput", "r")
                output = f.readlines()
                f.close()
            else:
                child.kill()
                error = "Command terminated by signal "+str(abs(code))
        except subprocess.TimeoutExpired:
            child.kill()
            error = "Time Limit Exceeded"
        except Exception as e:
            child.kill()
            error = str(e)

        return json.dumps({"error": error, "output": output, "time": executionTime})
    return render_template("home.html", title="Compiler", form=form)

