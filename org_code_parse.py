org_codes = open('org_codes_option.txt', 'r')
for line in org_codes:
    str = line.split('"')[1]
    str += " " + line.split('>')[1].split('<')[0]
    print(str)
    