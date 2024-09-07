from rapidocr_onnxruntime import RapidOCR
from PIL import Image
import streamlit as st
import pandas as pd

d = ["Survey:", "Se", "We", "Me", "In", "XL", "RC to", "Le", "on sei", "La", "Pre", "Sig", "Wav", "Tim"]
d1 = ["Survey", "Seismic", "Well", "Method", "InLine", "XLine", "Start time on RC", "Length of data window", "Start time on seismic", "Lag from RC to seismic", "Predictability", "Signal to Noise", "Wavelet phase(deg)", "Time(ms)"]
  
engine = RapidOCR(text_score=0.15)

def get_data(img_path):
    data = {}
    for i in d1:
        data[i] = None
    
    result, elapse = engine('cache.png')
    
    start = []
    end = []
    for i in result:
        if str(i[-2]).startswith("Survey:"):
            start.append(i[0])
        elif str(i[-2]).startswith("Wav"):
            end.append(i[0])
    #st.write(end)
    image = Image.open(img_path)
    delta = (end[0][-1][-1]-start[0][0][-1])//8
    cropped_image = image.crop((start[0][0][0]-delta, start[0][0][-1], image.size[0], end[0][-1][-1]+delta))
    cropped_image.save('cache.png')

    result, elapse = engine('cache.png')

    for i, j in enumerate(result):
        for m in d:
            if m in str(j[-2]):
                try:
                    try:
                        data[d1[d.index(m)]] = float(result[i+1][-2])
                    except:
                        data[d1[d.index(m)]] = result[i+1][-2].strip()
                except:
                    pass
            else:
                pass
    
    x = " ".join([i[-2] for i in result])
    return data, x

cols = pd.DataFrame([[i, True] for i in d1], columns=["列名", "是否选择"])
DATA = []
with st.sidebar:
    st.markdown('<h1 style="text-align: center; font-size: 24px; color: white; background: #ff4b4b; border-radius: .5rem; margin-bottom: 15px;">图片数据提取系统</h1>', unsafe_allow_html=True)

    with st.form("upload"):
        files = st.file_uploader("**上传要提取的png图片(可同时上传多张图片)**", type=["png"], accept_multiple_files=True)
        col = st.data_editor(cols, hide_index=True, use_container_width=True, height=200)
        button = st.form_submit_button("开始识别", use_container_width=True)

with st.expander("**识别结果展示**", True):
    if button:
        st.markdown('''<style>
            [data-testid="stForm"] {
                pointer-events: none;
            }
            </style>''', unsafe_allow_html=True)
        N = len(files)
        k = 0
        my_bar = st.progress(0, text="正在识别...")
        for i in files:
            bytes_data = i.read()
            with open("cache.png", "wb") as f:
                f.write(bytes_data)
            try:
                data, x = get_data(img_path="cache.png")
                DATA.append(data)
                #st.info(i.name+"提取成功!")
            except:
                st.warning(i.name+"提取失败!")
            k = k+1
            my_bar.progress(k/N, text=i.name+"提取成功!")
        
        my_bar.empty()
    
        df = pd.DataFrame(DATA)
        st.dataframe(df[col[col["是否选择"]==True]["列名"].tolist()], use_container_width=True, height=300)
        
        df[col[col["是否选择"]==True]["列名"].tolist()].to_excel("cache.xlsx")
        with open("cache.xlsx", "rb") as f:
            d = f.read()
        st.download_button(
            label="下载结果",
            data=d,
            use_container_width=True,
            file_name="result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        button1 = st.button("清除结果", use_container_width=True)
        if button1:
            st.markdown('''<style>
                [data-testid="stForm"] {
                    pointer-events: auto;
                }
                </style>''', unsafe_allow_html=True)
    else:
        st.info("当前未进行识别")
        c = st.columns([1,3,1])
        c[1].image("https://oss.showapi.com/site/apiLogo/1274.png", use_column_width=True)


