import re

entry_file = open('test.txt', 'r')
entry_file_lines = entry_file.readlines()


cont = 0
for i in entry_file_lines:
    cont += 1
    cont_com = 0
    regpunto = re.search(r'[\.]$', i)
    print(i)
    if regpunto == None and i != "\n":
        if i.isupper():
            pass
        else:
            print("ALTO, ESTA SI Error FEO ", cont)

    for char in i:
        if char == ")":
            cont_com -= 1
        elif char == "(":
            cont_com += 1
        if cont_com < 0:
            break
    if cont_com != 0 or i.count('"') % 2 != 0:
        print("AQUI HAY UN ERROR")


# entry_file = open('test.txt', 'r')
# entry_file_lines = entry_file.read()
# lines = entry_file_lines.split("\n")
# noenter = [line for line in lines if line.strip() != ""]

# sinempty = ""
# cont = 0
# for line in noenter:
#     cont += 1
#     print(line)
#     regpunto = re.search(r'[\.]$', line)
#     # print(re.search(r'[\.]$', line))
#     if regpunto == None:
#         if line.isupper():
#             print("ESTA LINEA ERRORPERO ESTA BIEN ", cont)
#         else:
#             print("ALTO, ESTA SI ERROR FEO ", cont)
#     sinempty += line + "\n"

# print("---------------------------")
# print(sinempty)