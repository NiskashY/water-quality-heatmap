n = 16
A = 9

def f(m):
	return n / (m - A)


def g(m, A):
	sum = 0
	for i in range(n):
		sum = sum + 1 / (m - (i + 1))
	return sum


min_lst = []
for m in range(n+1,80):
	f_m = f(m)
	g_m = g(m, A)
	min_lst.append(abs(f_m - g_m))
	# print(f'{m};{f_m};{g_m};{f_m - g_m}')
	print(f'{m} {f_m} {g_m} {f_m - g_m}')


print ('Lowest diff =', min(min_lst), 'index =', n + min_lst.index(min(min_lst)) + 1)
	
