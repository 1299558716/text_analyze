import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
from pyecharts.charts import Pie
from pyecharts import options as opts
from collections import Counter
import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}

# 从URL获取文本内容并添加调试信息
def fetch_text_from_url(url):
    try:
        response = requests.get(url,headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ')
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        if not cleaned_text:  # 如果文本为空，则抛出异常
            raise ValueError("The fetched content is empty.")
        return cleaned_text
    except Exception as e:
        st.error(f"Error fetching content from {url}: {str(e)}")
        return ""

# 分析文本并返回最常见的20个单词及其频率
def analyze_text(text):
    words = re.findall(r'\w+', text.lower())
    if not words:  # 如果没有找到任何单词，则抛出异常
        raise ValueError("No words found in the provided text.")
    return dict(Counter(words).most_common(20))

# Plotly词云（模拟）
def plotly_word_cloud(top_20_words):
    wc = WordCloud(width=800, height=400).generate_from_frequencies(top_20_words)
    fig = px.imshow(wc.to_array(), binary_string=True)
    fig.update_layout(coloraxis_showscale=False, xaxis_visible=False, yaxis_visible=False)
    return fig

# Plotly柱状图
def plotly_bar_chart(top_20_words):
    fig = px.bar(x=list(top_20_words.keys()), y=list(top_20_words.values()), labels={'x': 'Words', 'y': 'Frequency'})
    fig.update_layout(title="Top 20 Words Frequency", xaxis_tickangle=-45)
    return fig

# Pyecharts饼图
def pyecharts_pie_chart(top_20_words):
    pie = Pie()
    pie.add("", list(top_20_words.items()))
    pie.set_global_opts(title_opts=opts.TitleOpts(title="Top 20 Words Distribution"))
    return pie.render_embed()

# Matplotlib柱状图
def matplotlib_bar_chart(top_20_words):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top_20_words.keys(), top_20_words.values())
    ax.set_title('Top 20 Words Frequency')
    ax.set_xlabel('Words')
    ax.set_ylabel('Frequency')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig

# Streamlit界面
st.title("文本分析工具")
url = st.text_input('请输入要分析的文本URL')

if url:
    try:
        text = fetch_text_from_url(url)
        if not text:
            st.warning("未能从提供的URL中获取有效文本。")
        else:
            top_20_words = analyze_text(text)

            chart_type = st.selectbox('选择要显示的图表类型', ['Word Cloud', 'Bar Chart (Plotly)', 'Bar Chart (Matplotlib)', 'Pie Chart'])
            if chart_type == 'Word Cloud':
                st.plotly_chart(plotly_word_cloud(top_20_words))
            elif chart_type == 'Bar Chart (Plotly)':
                st.plotly_chart(plotly_bar_chart(top_20_words))
            elif chart_type == 'Bar Chart (Matplotlib)':
                st.pyplot(matplotlib_bar_chart(top_20_words))
            elif chart_type == 'Pie Chart':
                st.components.v1.html(pyecharts_pie_chart(top_20_words), width=800, height=600)
    except Exception as e:
        st.error(f"发生错误: {str(e)}")