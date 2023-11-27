import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')


def get_total_count_by_hour_df(hour):
    hour_count = hour.groupby(by="hours").agg({"count_cr": ["sum"]})
    return hour_count


def count_by_day_df(day):
    day_count = day.query(str('dteday >= "2011-01-01" and dteday < "2012-12-31"'))
    return day_count


def total_registered_df(day):
    reg = day.groupby(by="dteday").agg({
        "registered": "sum"
    })
    reg = reg.reset_index()
    reg.rename(columns={
        "registered": "register_sum"
    }, inplace=True)
    return reg


def total_casual_df(day):
    cas = day.groupby(by="dteday").agg({
        "casual": ["sum"]
    })
    cas = cas.reset_index()
    cas.rename(columns={
        "casual": "casual_sum"
    }, inplace=True)
    return cas


def sum_order(hour):
    sum_order_items_df = hour.groupby("hours").count_cr.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df


def macem_season(day):
    season = day.groupby(by="season").count_cr.sum().reset_index()
    return season


days = pd.read_csv("new_day.csv")
hours = pd.read_csv("new_hour.csv")

datetime_columns = ["dteday"]
days.sort_values(by="dteday", inplace=True)
days.reset_index(inplace=True)

hours.sort_values(by="dteday", inplace=True)
hours.reset_index(inplace=True)

for column in datetime_columns:
    days[column] = pd.to_datetime(days[column])
    hours[column] = pd.to_datetime(hours[column])

min_date_days = days["dteday"].min()
max_date_days = days["dteday"].max()

min_date_hour = hours["dteday"].min()
max_date_hour = hours["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("bike sharing logo.jpg")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days])

main_df_days = days[(days["dteday"] >= str(start_date)) &
                       (days["dteday"] <= str(end_date))]

main_df_hour = hours[(hours["dteday"] >= str(start_date)) &
                        (hours["dteday"] <= str(end_date))]

hour_count = get_total_count_by_hour_df(main_df_hour)
day_df_count = count_by_day_df(main_df_days)
reg = total_registered_df(main_df_days)
cas = total_casual_df(main_df_days)
sum_order_items_df = sum_order(main_df_hour)
season = macem_season(main_df_hour)

# Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Bike Sharing')

st.subheader('Bike Sharing Statistics')
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = day_df_count.count_cr.sum()
    st.metric("Jumlah Bike Sharing", value=total_orders)

with col2:
    total_sum = reg.register_sum.sum()
    st.metric("Jumlah Pengguna Registered", value=total_sum)

with col3:
    total_sum = cas.casual_sum.sum()
    st.metric("Jumlah Pengguna Casual", value=total_sum)

st.subheader("Perbandingan jumlah pengguna bike sharing yang registered dan casual")

labels = 'casual', 'registered'
sizes = [18.8, 81.2]
explode = (0, 0.1)

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', colors=["#a4a2a8", "#ea5545"],
        shadow=True)
ax1.axis('equal')

st.pyplot(fig1)

st.subheader("Perbandingan pengguna bike sharing pada hari libur dan hari kerja")

# Mengkategorikan data hari libur dan hari kerja
data_libur = hours[hours['holiday'] == 1]
data_kerja = hours[hours['holiday'] == 0]

# Rata-rata jumlah data untuk penyewaan sepeda pada hari libur dan hari kerja
penyewaan_libur = data_libur[['count_cr']].mean()
penyewaan_kerja = data_kerja[['count_cr']].mean()

# Data untuk visualisasi
fig, ax = plt.subplots()
categories = ['Total']
bar_width = 0.35
index = range(len(categories))

bar1 = ax.bar(index, penyewaan_libur, bar_width, label='Hari Libur', color="#a4a2a8")
bar2 = ax.bar([i + bar_width for i in index], penyewaan_kerja, bar_width, label='Hari Kerja',color="#b30000")
ax.set_xlabel('Kategori')
ax.set_ylabel('Rata-rata')
ax.set_title('Perbandingan pengguna bike sharing pada hari libur dan hari kerja')
ax.set_xticks([i + bar_width / 2 for i in index])
ax.set_xticklabels(categories)
ax.legend()
st.pyplot(fig)

st.subheader("Musim dengan jumlah pengguna bike sharing terbanyak")

colors = ["#b30000", "#a4a2a8", "#a4a2a8", "#a4a2a8"]
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    y="count_cr",
    x="season",
    data=season.sort_values(by="season",ascending=True),
    palette=colors,
    ax=ax
)
ax.set_title("Musim-musim", loc="center", fontsize=50)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='x', labelsize=35)
ax.tick_params(axis='y', labelsize=30)
st.pyplot(fig)

st.subheader("Performa penjualan perusahaan dalam beberapa bulan terakhir")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    days["dteday"],
    days["count_cr"],
    color="#b30000",
    marker='o',
    linewidth=2,

)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Waktu dengan bike sharing terbanyak")
fig, ax = plt.subplots(figsize=(20, 10))

sns.barplot(x="hours", y="count_cr", data=sum_order_items_df.head(5),
            palette=["#a4a2a8", "#a4a2a8", "#b30000", "#a4a2a8", "#a4a2a8"], ax=ax)
ax.set_ylabel(None)
ax.set_xlabel("Hours (PM)", fontsize=30)
ax.set_title("Jam dengan banyak bike sharing", loc="center", fontsize=30)
ax.tick_params(axis='y', labelsize=35)
ax.tick_params(axis='x', labelsize=30)

st.pyplot(fig)

st.caption("Muhammad Fadli Ramadhan, TensorFlow Developer")


