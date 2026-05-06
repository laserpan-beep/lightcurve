import lightkurve as lk
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

search_result_33_120 = lk.search_targetpixelfile('HAT-P 24', exptime=120, sector=33)

tpf = search_result_33_120.download()

#Создание свой маски
custom_threshold_mask = tpf.create_threshold_mask(threshold=2)

#Инверсируем (~) маску порога, чтобы найти фон
bias = ~tpf.create_threshold_mask(threshold=0.1)

#Превращаем в кривую, надевая маску фона на кривую
bias_lk = tpf.to_lightcurve(aperture_mask=bias)

#Находим фон на один пиксель деля поток у фона на весь
MasterBias = (bias_lk.flux) / (bias.sum())

#Создаём наши кривые (У нас совпадают pipeline и threshold)
lc_pipe = tpf.to_lightcurve(aperture_mask='pipeline')
lc_thre = tpf.to_lightcurve(aperture_mask='threshold')
lc_cust = tpf.to_lightcurve(aperture_mask=custom_threshold_mask)

#Вычитаем фон из наших кривых
lc_pipe.flux = lc_pipe.flux - (MasterBias * tpf.pipeline_mask.sum())
lc_thre.flux = lc_thre.flux - (MasterBias * tpf.create_threshold_mask().sum())
lc_cust.flux = lc_cust.flux - (MasterBias * custom_threshold_mask.sum())

lc_pipe = lc_pipe.remove_outliers(sigma_lower=float('inf'), sigma_upper=3)
lc_thre = lc_thre.remove_outliers(sigma_lower=float('inf'), sigma_upper=3)
lc_cust = lc_cust.remove_outliers(sigma_lower=float('inf'), sigma_upper=3)

lcs = [lc_pipe, lc_thre, lc_cust]

#Создание графика
fig = plt.figure(figsize=(18, 10))
fig.suptitle('HAT-P 24')
gs = GridSpec(3, 6, figure=fig, hspace=0.4, wspace=0.4)

ax_raw = fig.add_subplot(gs[0, 0:3])
ax_bin = fig.add_subplot(gs[0, 3:6])

axes_period = [fig.add_subplot(gs[1, 0:2]), fig.add_subplot(gs[1, 2:4]), fig.add_subplot(gs[1, 4:6])]
axes_fold = [fig.add_subplot(gs[2, 0:2]), fig.add_subplot(gs[2, 2:4]), fig.add_subplot(gs[2, 4:6])]

#Отрисовка верхних графиков
lc_pipe.plot(ax=ax_raw, label='pipeline', linewidth=0.5, color='red')
lc_thre.plot(ax=ax_raw, label='threshold', linewidth=0.5, color='blue')
lc_cust.plot(ax=ax_raw, label='custom threshold', linewidth=0.5, color='green')

lc_pipe.plot(ax=ax_bin, label='pipeline', linewidth=0.5, color='red')
lc_thre.plot(ax=ax_bin, label='threshold', linewidth=0.5, color='blue')
lc_cust.plot(ax=ax_bin, label='custom threshold', linewidth=0.5, color='green')


k=0

#Будем вводить легенду графика через label и переменную k
label=''
#Cоздание пары i=0 lc=lc_pipe,...
for i, lc in enumerate(lcs):
    period = lc.to_periodogram(method="bls", minimum_period=1, maximum_period=5)
    MAX_period = period.period_at_max_power
    epoch=period.transit_time_at_max_power
    if k==0:
        label='pipeline'
    if k==1:
        label='threshold'
    if k==2:
        label='custom threshold'
    period.plot(ax=axes_period[i], color="red", label=(f'{label}','exptime=120', f'MAX period={MAX_period.value:.4f}'))

    lc_folded = lc.fold(period=MAX_period,epoch_time=epoch,normalize_phase=True)

    lc_folded.plot(ax=axes_fold[i], color='purple', label=(f'{label}','exptime=120'))

    axes_fold[i].set_title('Phase Curve')
    k+=1

plt.tight_layout()

plt.show()
