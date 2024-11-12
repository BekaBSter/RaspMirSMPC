def check_differences_content(last_content, new_content):
    last_content = last_content.split("\n")
    new_content = new_content.split("\n")
    difference_content = ""
    yellow_color = '''style="background-color: #FFCF63'''
    red_color = '''style="background-color: #FF0000'''
    if len(last_content) == len(new_content):
        print("last equal new")
        for i in range(0, len(last_content)):
            if last_content[i] != new_content[i]:
                new_content[i] = new_content[i].replace(yellow_color, red_color)
            difference_content = difference_content + "\n" + new_content[i]
    else:
        print("last not equal new")
        for i in range(0, min(len(last_content), len(new_content))):
            if last_content[i] != new_content[i]:
                new_content[i] = new_content[i].replace(yellow_color, red_color)
            difference_content = difference_content + "\n" + new_content[i]
        for i in range(min(len(last_content), len(new_content)), max(len(last_content), len(new_content))):
            new_content[i] = new_content[i].replace(yellow_color, red_color)
            difference_content = difference_content + "\n" + new_content[i]
    return difference_content


new_content = open("files/1_new.html").read()
last_content = open("files/1_last.html").read()
print(new_content)
print(last_content)
differences = check_differences_content(last_content, new_content)
with open("files/1_differences.html", "w") as file_dif:
    file_dif.write(differences)
