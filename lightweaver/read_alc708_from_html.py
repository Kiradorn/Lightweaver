'''
Routine for reading the table data from the ALC7 IOP page, correcting for formatting error, and saving to .npz
'''

#May lead to problems if the IOP page detects that it's automated software. Currently leads to a Captcha. Recommended to run and then save the output to a npz file.
driver = webdriver.Chrome()
driver.get("https://iopscience.iop.org/article/10.1086/523671/fulltext/tb26.html")
html = driver.page_source
# driver.quit()

table_alc7 = pd.read_html(html)
len(table_alc7)
table_alc7[1].head()

table_alc7[1].columns=['index','height','cmass','temperature','velocity','pressure_gas','pressure_total','n_H','n_H1','n_e']
table_alc7[1].drop([0],axis=0, inplace=True)
table_alc7[1].drop(['index'],axis=1, inplace=True)
annoyingMinus=table_alc7[1]['height'][140][0]
table_alc7[1]['height']=table_alc7[1].height.str.replace(annoyingMinus, '-', regex=True) # Replaces stupid '-' symbol that isn't interpreted as a minus sign
table_alc7[1]['cmass']=table_alc7[1].cmass.str.replace(annoyingMinus, '-', regex=True) # Replaces stupid '-' symbol that isn't interpreted as a minus sign
table_alc7[1]['temperature']=table_alc7[1].temperature.str.replace(annoyingMinus, '-', regex=True) # Replaces stupid '-' symbol that isn't interpreted as a minus sign
table_alc7[1]['velocity']=table_alc7[1].velocity.str.replace(annoyingMinus, '-', regex=True) # Replaces stupid '-' symbol that isn't interpreted as a minus sign
table_alc7[1]['pressure_gas']=table_alc7[1].pressure_gas.str.replace(annoyingMinus, '-', regex=True) # Replaces stupid '-' symbol that isn't interpreted as a minus sign
table_alc7[1]['pressure_total']=table_alc7[1].pressure_total.str.replace(annoyingMinus, '-', regex=True) # Replaces stupid '-' symbol that isn't interpreted as a minus sign
table_alc7[1]['n_H']=table_alc7[1].n_H.str.replace(annoyingMinus, '-', regex=True) # Replaces stupid '-' symbol that isn't interpreted as a minus sign
table_alc7[1]['n_H1']=table_alc7[1].n_H1.str.replace(annoyingMinus, '-', regex=True) # Replaces stupid '-' symbol that isn't interpreted as a minus sign
table_alc7[1]['n_e']=table_alc7[1].n_e.str.replace(annoyingMinus, '-', regex=True) # Replaces stupid '-' symbol that isn't interpreted as a minus sign

#errors=coerce forces the routine to interpret the string as a number but can lead to errors such as NaN
height=(pd.to_numeric(table_alc7[1].height, errors='coerce').to_numpy()*astropy.units.km).si.value
cmass=(pd.to_numeric(table_alc7[1].cmass, errors='coerce').to_numpy()*astropy.units.g*astropy.units.cm**-2).si.value
temperature=pd.to_numeric(table_alc7[1].temperature, errors='coerce').to_numpy()
velocity=(pd.to_numeric(table_alc7[1].velocity, errors='coerce').to_numpy()*astropy.units.km*astropy.units.s**-1).si.value
pressure_gas=(pd.to_numeric(table_alc7[1].pressure_gas, errors='coerce').to_numpy()*astropy.units.dyn*astropy.units.cm**-2).si.value
pressure_total=(pd.to_numeric(table_alc7[1].pressure_total, errors='coerce').to_numpy()*astropy.units.dyn*astropy.units.cm**-2).si.value
n_H=(pd.to_numeric(table_alc7[1].n_H, errors='coerce').to_numpy()*astropy.units.cm**-3).si.value
n_H1=(pd.to_numeric(table_alc7[1].n_H1, errors='coerce').to_numpy()*astropy.units.cm**-3).si.value
n_e=(pd.to_numeric(table_alc7[1].n_e, errors='coerce').to_numpy()*astropy.units.cm**-3).si.value

log10_n_H=[16.0,15.5,15.0,14.5,14.0,13.5,13.0,12.5,12.0,11.8,11.5,11.3,11.0,10.8,10.5,10.3,10.0,9.8,9.5,9.3,9.0]
vnt=[0.34,0.37,0.4,0.5,0.6,0.7,1.0,1.5,2.5,3.1,3.8,4.7,6.0,7.6,9.3,11.4,15.0,19.8,24.5,29.3,34.]
vnt_interpd=interpolate.InterpolatedUnivariateSpline(log10_n_H[::-1],vnt[::-1])
vturb=vnt_interpd(np.log10(((n_H+n_H1)*astropy.units.m**-3).cgs.value))

#adhoc modification to get low altitude correction to vturb profile
vturb_from_pressure=np.sqrt(2*(pressure_total-pressure_gas)/((n_H+n_H1)*astropy.constants.m_p.value))
vturb[np.log10(((n_H+n_H1)*astropy.units.m**-3).cgs.value)<9.]=34
vturb[(height/1e6)<0.5]=vturb_from_pressure[(height/1e6)<0.5]/1000
vturb=(vturb*astropy.units.km*astropy.units.s**-1).si.value

plt.figure(figsize=(10,10))
plt.plot(height/1e6, temperature)
plt.plot(height/1e6, vturb2/1000)
plt.xlim(0,3)
plt.yscale('log')
plt.ylim(0,4000)
plt.axhline(10000)
plt.plot(log10_n_H,vnt)

# print(temperature[0])

np.savez('/Volumes/TRANSCEND/Projects/amrvac/synthesised_spectra/alc7.npz', height=height, cmass=cmass, temperature=temperature, velocity=velocity, vturb=vturb, pressure_gas=pressure_gas, pressure_total=pressure_total, n_H=n_H, n_H1=n_H1, n_e=n_e)