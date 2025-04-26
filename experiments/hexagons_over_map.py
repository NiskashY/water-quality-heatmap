import ellipsis as el

pathId = '1a24a1ee-7f39-4d21-b149-88df5a3b633a'
timestampId = '45c47c8a-035e-429a-9ace-2dff1956e8d9'

sh_countries = el.path.vector.timestamp.listFeatures(pathId, timestampId)['result']

sh_usa = sh_countries[sh_countries['NAME'] == 'United States']
sh_usa.plot()