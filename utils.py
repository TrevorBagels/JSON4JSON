def seperate_string_number(string):
	previous_character = string[0]
	groups = []
	alsonumeric = [".", "-"]
	newword = string[0]
	for x, i in enumerate(string[1:]):
		if i.isalpha() and previous_character.isalpha():
			newword += i
		elif (i.isnumeric() or i in alsonumeric) and (previous_character.isnumeric() or previous_character in alsonumeric):
			newword += i
		else:
			groups.append(newword)
			newword = i

		previous_character = i

		if x == len(string) - 2:
			groups.append(newword)
			newword = ''
	return groups