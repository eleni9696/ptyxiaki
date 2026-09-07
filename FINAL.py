# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 12:15:23 2026

@author: shade
"""
#%% PACKAGES

import numpy
import pandas
import xarray
import cartopy.crs as ccrs
import cdsapi
import matplotlib.pyplot
import scipy.stats
import statsmodels.api
import pymannkendall as mk


#%% DOWNLOAD ΔΕΔΟΜΕΝΑ


rotated_pole = ccrs.RotatedPole(pole_longitude=-162.0, pole_latitude=39.25)
wlon, nlat, elon, slat = [19.3, 41.7, 28.3, 34.7]
wrlon, nrlat = rotated_pole.transform_point(wlon, nlat, ccrs.Geodetic())
erlon, srlat = rotated_pole.transform_point(elon, slat, ccrs.Geodetic())

variables = ["2m_relative_humidity",
              "10m_wind_speed",
              "maximum_2m_temperature_in_the_last_24_hours",
              "mean_precipitation_flux",
              "total_cloud_cover"]
dataset = "projections-cordex-domains-single-levels"
client = cdsapi.Client()
for v in variables:
    print("=========================================================")
    print("Requesting ", v)
    request = {
        "domain": "europe",
        "experiment": "rcp_2_6", #αλλαγή για 8.5
        "horizontal_resolution": "0_11_degree_x_0_11_degree",
        "temporal_resolution": "daily_mean",
        "variable": v,
        "gcm_model": "mpi_m_mpi_esm_lr",
        "rcm_model": "knmi_racmo22e",
        "ensemble_member": "r1i1p1",
        "start_year": [
            "2026",
            "2031",
            "2036",
            "2041",
            "2046",
            "2051",
            "2056",
            "2061",
            "2066",
            "2071"
        ],
        "end_year": [
            "2030",
            "2035",
            "2040",
            "2045",
            "2050",
            "2055",
            "2060",
            "2065",
            "2070",
            "2075"
            ],
        "area": [nrlat, wrlon, srlat, erlon],
    }
    client.retrieve(dataset, request).download()



#%% ΑΔΕΙΟ DSGEN


fname = "C:/pythondata/rcp26/clt/clt_EUR-11_MPI-M-MPI-ESM-LR_rcp26_r1i1p1_KNMI-RACMO22E_v1_day_20260101-20301231.area-subset.-9.041365803697806.8.77209750264492.-15.43923932127278.0.9828051688188043.nc"
cloud = xarray.open_dataset (fname)

start_year = 2026
end_year = 2075
times = pandas.date_range(start=f"{start_year}-01-01", end=f"{end_year}-12-31", 
                      freq='D')

DSGEN = xarray.Dataset( 
    data_vars={
        "rotated_pole" : cloud.rotated_pole,
        "clt" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)), #σύννεφα σε %
        "tasmax" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),  #θερμοκρασία σε Kelvin
        "pr" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),  #βροχόπτωση σε kg m^-2 s^-1
        "sfcWind" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),  #ταχύτητα σε αέρα m/s
        "hurs" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),  #υγρασία σε %
        "ET" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),  #ειδική θερμοκρασία
        "Ts" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),
        "Ts_rank" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),
        "clt_rank" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),
        "pr_rank" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),
        "sfcWind_rank" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),
        "ET_rank" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),
        "HCI" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan)),  
        "CIT" : (["time", "rlat", "rlon"],
                numpy.full((len(times), len(cloud.rlat), len(cloud.rlon)), numpy.nan))
    },
    coords={
        "time" : times,
        "rlat" : cloud.rlat,
        "rlon" : cloud.rlon,
        "lat": (["rlat", "rlon"], cloud.lat.data),
        "lon": (["rlat", "rlon"], cloud.lon.data),
    },
    attrs={"description": "Data for rcp 2.6"} #αλλαγή για 2.6 ή 8.5
)

    


#%% ΓΕΜΙΖΟΥΜΕ ΤΟ DSGEN

rcp="rcp26" #αλλαγή για 2.6 ή 8.5
quantities = ["clt", "tasmax", "pr", "sfcWind", "hurs"]
for qu in quantities:
    for yr in range(start_year, end_year+1, 5):
        fname = f'C:/pythondata/{rcp}/{qu}/{qu}_EUR-11_MPI-M-MPI-ESM-LR_{rcp}_r1i1p1_KNMI-RACMO22E_v1_day_{yr}0101-{yr+4}1231.area-subset.-9.041365803697806.8.77209750264492.-15.43923932127278.0.9828051688188043.nc'
        ds = xarray.open_dataset(fname)
        print(f"Reading {qu}, year {yr}")
    
        DSGEN[qu].loc[{"time": slice(f"{yr}-01-01", f"{yr+4}-12-31")}] = ds[qu].values
            
        if "height" in ds[qu].coords: 
            DSGEN[qu].attrs["height"] = ds[qu].height.values
            
            

#%% CIT

#μεταρτοπές/υπολογισμοί
DSGEN["tasmax"] = DSGEN["tasmax"] - 273.15  #μετατροπή σε C
DSGEN["pr"] = DSGEN["pr"]*24*60*60  #μετατροπή σε mm/d

h = 0.008  # in cm
M = 25  # in cal/s
A = 0.45  # albedo of clothing/skin
sun = (100.0-DSGEN["clt"])/100  # proportion of daylight hours with sunshine
DSGEN["Ts"] = DSGEN["tasmax"] + 1/7*h*M + (M-15 + 120*sun*(1-A)) / (2 + 9*(0.1+DSGEN["sfcWind"])**0.5)

#rank
DSGEN["Ts_rank"] = xarray.where(
    DSGEN["Ts"] > 35.5,
    +4,
    xarray.where(
        (DSGEN["Ts"] <= 35.5) & (DSGEN["Ts"] > 34.5),
        +3,
        xarray.where(
            (DSGEN["Ts"] <= 34.5) & (DSGEN["Ts"] > 33.5),
            +2,
            xarray.where(
                (DSGEN["Ts"] <= 33.5) & (DSGEN["Ts"] > 32.5),
                +1,
                xarray.where(
                    (DSGEN["Ts"] <= 32.5) & (DSGEN["Ts"] > 31),
                    0,
                    xarray.where(
                        (DSGEN["Ts"] <= 31) & (DSGEN["Ts"] > 29),
                        -1,
                        xarray.where(
                            (DSGEN["Ts"] <= 29) & (DSGEN["Ts"] > 26),
                            -2,
                            xarray.where(
                                (DSGEN["Ts"] <= 26) & (DSGEN["Ts"] >= 21),
                                -3,
                                xarray.where(
                                    (DSGEN["Ts"] < 21),
                                    -4,
                                    numpy.nan
)))))))))


#calculate
def calculate (RAIN, TSR, WN, CC):
    if RAIN > 3:
        if +2 <= TSR <= +4:
            return 2
        else:
            return 1
    elif WN >= 6:
        if TSR == +4:
            return 3
        elif +1 <= TSR <= +3:
            return 4
        elif -1 <= TSR <= 0:
            return 2
        else:
            return 1
    elif  CC>=50:
        if TSR == +4 or (-1 <=TSR<= 0):
            return 3
        elif +2 <= TSR <= +3:
            return 5
        elif TSR== +1:
            return 4
        else: 
            return 1
    elif  CC<=40:
            if TSR == +4 or TSR == -1:
                return 4
            elif TSR == +3 or TSR == +1:
                return 6
            elif TSR == 0:
                return 5
            elif TSR == +2:
                return 7
            else:
                return 1
    else:
        return numpy.nan
    
DSGEN["CIT"] = xarray.apply_ufunc(
    calculate, 
    DSGEN["pr"], 
    DSGEN["Ts_rank"],
    DSGEN["sfcWind"],
    DSGEN["clt"],
    vectorize=True,
    output_dtypes=[float]
    )
        
         

#%% HCI

#μετατροπές/υπολογισμοί
DSGEN["sfcWind"] = DSGEN["sfcWind"]*3.6  #μετατροπή σε km/h
DSGEN["ET"] = DSGEN["tasmax"] - ((0.4 * (DSGEN["tasmax"]-10)) * (1-(DSGEN["hurs"])/100))

#rank
DSGEN["clt_rank"] = xarray.where(
    DSGEN["clt"] == 100,
    1,
    xarray.where(
        (DSGEN["clt"] < 100) & (DSGEN["clt"] > 90),
        2,
        xarray.where(
            (DSGEN["clt"] <= 90) & (DSGEN["clt"] > 80),
            3,
            xarray.where(
                (DSGEN["clt"] <= 80) & (DSGEN["clt"] > 70),
                4,
                xarray.where(
                    (DSGEN["clt"] <= 70) & (DSGEN["clt"] > 60),
                    5,
                    xarray.where(
                        (DSGEN["clt"] <= 60) & (DSGEN["clt"] > 50),
                        6,
                        xarray.where(
                            (DSGEN["clt"] <= 50) & (DSGEN["clt"] > 40),
                            7,
                            xarray.where(
                                ((DSGEN["clt"] <= 40) & (DSGEN["clt"] > 30)) | (DSGEN["clt"]==0),
                                8,
                                xarray.where(
                                    ((DSGEN["clt"] <= 30) & (DSGEN["clt"] > 20)) | ((DSGEN["clt"] <= 10) & (DSGEN["clt"] > 0)),
                                    9,
                                    xarray.where(
                                        (DSGEN["clt"] <= 20) & (DSGEN["clt"] > 10),
                                        10,
                                        numpy.nan
))))))))))
    
   
DSGEN["pr_rank"] = xarray.where(
    DSGEN["pr"] > 25,
    -1,
    xarray.where(
        (DSGEN["pr"] <= 25) & (DSGEN["pr"] >= 12),
        0,
        xarray.where(
            (DSGEN["pr"] < 12) & (DSGEN["pr"] >= 9),
            2,
            xarray.where(
                (DSGEN["pr"] < 9) & (DSGEN["pr"] >= 6),
                5,
                xarray.where(
                    (DSGEN["pr"] < 6) & (DSGEN["pr"] >= 3),
                    8,
                    xarray.where(
                        (DSGEN["pr"] < 3) & (DSGEN["pr"] > 0),
                        9,
                        xarray.where(
                            (DSGEN["pr"] == 0),
                            10,
                            numpy.nan
)))))))
    
    
DSGEN["sfcWind_rank"] = xarray.where(
    DSGEN["sfcWind"] > 70,
    -10,
    xarray.where(
        (DSGEN["sfcWind"] <= 70) & (DSGEN["sfcWind"] >= 50),
        0,
        xarray.where(
            (DSGEN["sfcWind"] < 50) & (DSGEN["sfcWind"] >= 40),
            3,
            xarray.where(
                (DSGEN["sfcWind"] < 40) & (DSGEN["sfcWind"] >= 30),
                6,
                xarray.where(
                    ((DSGEN["sfcWind"] < 30) & (DSGEN["sfcWind"] >= 20)) | (DSGEN["sfcWind"] == 0),
                    8,
                    xarray.where(
                        (DSGEN["sfcWind"] < 20) & (DSGEN["sfcWind"] >= 10),
                        9,
                        xarray.where(
                            (DSGEN["sfcWind"] < 10) & (DSGEN["sfcWind"] > 0),
                            10,
                            numpy.nan
)))))))


DSGEN["ET_rank"] = xarray.where(
    DSGEN["ET"] >= 39,
    0,
    xarray.where(
        (DSGEN["ET"] <= -6),
        1,
        xarray.where(
            ((DSGEN["ET"] < 0) & (DSGEN["ET"] > -6)) | ((DSGEN["ET"] < 39) & (DSGEN["ET"] >= 37)),
            2,
            xarray.where(
                (DSGEN["ET"] < 7) & (DSGEN["ET"] >= 0),
                3,
                xarray.where(
                    ((DSGEN["ET"] < 11) & (DSGEN["ET"] >= 6)) | ((DSGEN["ET"] < 37) & (DSGEN["ET"] >= 35)),
                    4,
                    xarray.where(
                        ((DSGEN["ET"] < 15) & (DSGEN["ET"] >= 11)) | ((DSGEN["ET"] < 35) & (DSGEN["ET"] >= 33)),
                        5,
                        xarray.where(
                            ((DSGEN["ET"] < 18) & (DSGEN["ET"] >= 15)) | ((DSGEN["ET"] < 33) & (DSGEN["ET"] >= 31)),
                            6,
                            xarray.where(
                                ((DSGEN["ET"] < 20) & (DSGEN["ET"] >= 18)) | ((DSGEN["ET"] < 31) & (DSGEN["ET"] >= 29)),
                                7,
                                xarray.where(
                                    (DSGEN["ET"] < 29) & (DSGEN["ET"] >= 27),
                                    8,
                                    xarray.where(
                                        ((DSGEN["ET"] < 23) & (DSGEN["ET"] >= 20)) | ((DSGEN["ET"] < 27) & (DSGEN["ET"] >= 26)),
                                        9,
                                        xarray.where(
                                            (DSGEN["ET"] < 26) & (DSGEN["ET"] >= 23),
                                            10,
                                            numpy.nan
)))))))))))

#calculate
DSGEN["HCI"] = 4*DSGEN["ET_rank"] + 2*DSGEN["clt_rank"] + 3*DSGEN["pr_rank"] + DSGEN["sfcWind_rank"]


       
#%% DS26
DS26 = DSGEN.copy()

#%%DS85
DS85 = DSGEN.copy()

#%% ΑΠΟΤΕΛΕΣΜΑΤΑ

dst = {26: DS26,
       85: DS85}


var1 = "HCI"
label1 = "2026-2050"
dst1 = dst[85]

var2 = "HCI"
label2 = "2051-2075"
dst2 = dst[85]

#χάρτης
var3 = "HCI" 
label3 = "HCI"
dst3 = dst[85]

gb = "time.year" # ή time.month
title = "Μέσο HCI 2051-2075 (RCP 8.5)"
labelx = "Rotated Longtitude"
labely = "Rotated Latitude"



PlotTime1 = (dst1[var1].#sel(time=DSGEN.time.dt.month.isin([5,6,7,8,9])). #1-12
             sel(time=slice("2026","2050")).
             groupby(gb).mean(dim=["time", "rlat", "rlon"]))#.plot(
matplotlib.pyplot.plot(
    numpy.arange(len(PlotTime1)),
    PlotTime1,
    color="red", 
    linewidth=1, 
    #marker= "o", 
    #markersize=0.5, 
    linestyle="-",
    label= label1)

PlotTime2 = (dst2[var2].#sel(time=DSGEN.time.dt.month.isin([5,6,7,8,9])). #1-12
             sel(time=slice("2051","2075")).
             groupby(gb).mean(dim=["time", "rlat", "rlon"]))#.plot(
matplotlib.pyplot.plot(
    numpy.arange(len(PlotTime2)),
    PlotTime2,
    color="blue", 
    linewidth=1, 
    #marker= "o", 
    #markersize=0.5, 
    linestyle="-",
    label= label2)
 
                 
matplotlib.pyplot.grid()
matplotlib.pyplot.legend()
matplotlib.pyplot.xticks(range(0,12),["Ιαν.", "Φεβ.", "Μάρ.", "Απρ.", "Μάι.", "Ιούν.", "Ιούλ.", "Αύγ.", "Σεπτ.", "Οκτ.", "Νοέ.", "Δεκ."]) #numpy.arange(0,25,5) ή numpy.arange(2026,2075,5) ή range(0,12),["Ιαν.", "Φεβ.", "Μάρ.", "Απρ.", "Μάι.", "Ιούν.", "Ιούλ.", "Αύγ.", "Σεπτ.", "Οκτ.", "Νοέ.", "Δεκ."]
#matplotlib.pyplot.yticks(numpy.arange(,,,))
matplotlib.pyplot.xlim(left=0, right=11) # (left=0, right=25) ή (left=2026, right=2075) ή (left=0, right=11)
#matplotlib.pyplot.ylim()

#χάρτης
PlotTime3 = (dst3[var3].#sel(time=DSGEN.time.dt.month.isin([5,6,7,8,9])). #1-12
             sel(time=slice("2051","2075")).mean(dim="time").
             plot(
                     cmap="viridis",
                     vmin=60, #95-70 σεζον, 85-60 ετησιο HCI
                     vmax=95,
                     #x="lon",
                     #y="lat",
                     cbar_kwargs={"label":label3}))


matplotlib.pyplot.title(title,
                        fontsize=18,
                        fontweight= "bold")
matplotlib.pyplot.xlabel(labelx,
                         fontsize=12)
matplotlib.pyplot.ylabel(labely,
                         fontsize=12)
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.show()



#%% ΣΤΑΤΙΣΤΙΚΟΙ ΕΛΕΓΧΟΙ

check = (dst2[var2].
             #sel(time=DSGEN.time.dt.month.isin([6,7,8])). #1-12
             #sel(time=slice("2026","2050")).
             groupby(gb).mean(dim=["time", "rlat", "rlon"]))

#Shapiro-Wilk normality test
from scipy.stats import shapiro
stat, p = shapiro(check)

if p > 0.05:
    print ("Number:", stat)
    print ("P value:", p)
    print ("Probably normal distribution")
else:
   print ("Number:", stat)
   print ("P value:", p)
   print ("Not normal distribution") 
   
   
#Q-Q plot
scipy.stats.probplot((check).values,
             dist="norm", plot=matplotlib.pyplot)
matplotlib.pyplot.title("Q-Q plot RCP 2.6",
                        fontsize=18,
                        fontweight= "bold")
matplotlib.pyplot.grid()
matplotlib.pyplot.tight_layout()
matplotlib.pyplot.show()


#OLS regression
def fit_regression(y, x):
    if numpy.count_nonzero(~numpy.isnan(y))>2:
         model = statsmodels.api.OLS(endog=y[(~numpy.isnan(y))], exog= statsmodels.api.add_constant(x[(~numpy.isnan(y))]))
         results = model.fit()
         return results.pvalues[1], results.params[1]*10  # *365.25 per decade if check dims is time, without if check.dims is year
    else:
         return numpy.nan, numpy.nan


# Calculate the anomalies
climatology = (dst2[var2].
             #sel(time=DSGEN.time.dt.month.isin([6,7,8])). #1-12
             #sel(time=slice("2026","2050")).
             groupby(gb).mean(dim=["time", "rlat", "rlon"]))
anomalies = (dst2[var2].
             #sel(time=DSGEN.time.dt.month.isin([6,7,8])). #1-12
             #sel(time=slice("2026","2050")).
             groupby(gb)) - climatology      #without the mean


#x = (DSGEN.time - DSGEN.time.isel(time=0))/numpy.timedelta64(1, "D") #if check.dims is time
x = check.year - check.year[0] #if check.dims is year
pvalueOLS, slopeOLS = xarray.apply_ufunc(
        fit_regression,
        #anomalies, x,  #anomalies 
        check, x,      #raw data
        input_core_dims=[['year'], ['year']],  # time/year change depending on check.dims
        output_core_dims=[[], []],
        vectorize=True, 
        dask='parallelized',  
        output_dtypes=[float, float],
    )
slopeOLS = slopeOLS.assign_attrs(units="per decade")


print (f"OLS P-value is {pvalueOLS.item():.6f}")
print (f"OLS Slope is {slopeOLS.item():.6f}")

intercept1 = check.mean() - slopeOLS / 10  * x.mean()
OLSline1= intercept1 + slopeOLS/10 * x
OLSline1.plot(color = "darkred", label = "RCP 8.5 OLS slope")

intercept2 = check.mean() - slopeOLS / 10  * x.mean()
OLSline2= intercept2 + slopeOLS/10 * x
OLSline2.plot(color = "darkblue", label = "RCP 2.6 OLS slope")

del x


#Mann-Kendall regression and Sen's slope
# MK is applied ONLY on the annual mean
def mk_regression(y):
    if numpy.count_nonzero(~numpy.isnan(y))>2:
        result = mk.original_test(y[~numpy.isnan(y)])
        return result.p, result.slope*10 # per decade
    else:
         return numpy.nan, numpy.nan


pvalueMK, slopeMK = xarray.apply_ufunc(
            mk_regression,
            check,
            input_core_dims=[['year']],  # iterate over lat/lon
            output_core_dims=[[], []],
            vectorize=True,  
            dask='parallelized',  
            output_dtypes=[float, float],
            )
slopeMK = slopeMK.assign_attrs(units="per decade")


print (f"MK P-value is {pvalueMK.item():.6f}")
print (f"MK Slope is {slopeMK.item():.6f}")



#%% πρόχειρο           
print(DSGEN["CIT"].sel(time="2055-09-07").sel(rlat=-9.295).sel(rlon=1.215)) 
print(DSGEN.isnull().any())     
     
DSGEN["CIT"].where(
    (DSGEN["lat"]>=38.99) & (DSGEN["lat"]<=39.40) & (DSGEN["lon"]<=26.64) & (DSGEN["lon"]>=25.85),
    drop=True).isel(time=6767).plot()
matplotlib.pyplot.show()


count = (DSGEN["CIT"]==5).sum()
print(count.values)




