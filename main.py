import lightkurve as lk
import matplotlib.pyplot as plt

#Ищем наш результат для сектора 33, exptime=20,120 (единственные объекты)
search_result_33_20=lk.search_lightcurve('HAT-P 24',exptime=20,sector=33)
search_result_33_120=lk.search_lightcurve('HAT-P 24',exptime=120,sector=33)
#Отрезаем последний элемент (их 2)
search_result_33_600=lk.search_lightcurve('HAT-P 24',exptime=600,sector=33)[:-1]

search_result_33=[search_result_33_20,search_result_33_120,search_result_33_600]
lcs=[]
for i in range(3):
    lc=search_result_33[i].download()
    lcs.append(lc)


fig, axes = plt.subplots(3,4, figsize=(20,10))
k=20
#Прохождение по lcs парой, то есть i=0 => lc=search_result_33_20,...
for i,lc in enumerate(lcs):
    #Изменение exptime по типу рекурсии
    if k==120:
        k=600
    if k==20 and i!=0:
        k=120
    lc.plot(ax=axes[i,0],color="blue",label=f'exptime={k}')

    lc_sigma=lc.remove_nans().remove_outliers(sigma=5)
    lc_sigma.plot(ax=axes[i,1],color="green",label=f'exptime={k}')

    #Нахождение периода методом Ломб-Скаргла
    period=lc_sigma.to_periodogram(method="Lombscargle",minimum_period=1,maximum_period=20)
    MAX_period=period.period_at_max_power
    period.plot(ax=axes[i,2],color="red",label=(f'exptime={k}', f'MAX period={MAX_period:.4f} '))

    #Сворачивание кривых блеса с найденным МАКСимальным периодом
    lc_folded=lc_sigma.fold(period=MAX_period)
    lc_folded.plot(ax=axes[i,3],color='purple',label=f'exptime={k}')

plt.tight_layout()

plt.show()





