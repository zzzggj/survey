import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_cookies_manager import EncryptedCookieManager

# Cookie 一人一票限制
cookies = EncryptedCookieManager(
    password="canteen20260425abc",
    prefix="canteen_survey/"
)
if not cookies.ready():
    st.stop()

# 隐藏多余元素
hide_menu_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display:none;}
</style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.set_page_config(page_title="食堂满意度调查", layout="centered")
st.title("员工食堂满意度调查")
csv_file = "survey_results.csv"

# 你指定的问题顺序+选项
questions_config = {
    "1. 饭菜新鲜度": ["新鲜", "还可以", "偶尔不新鲜"],
    "2. 异物发现情况": ["没发现过", "没注意", "偶尔发现"],
    "3. 汤味道": ["好喝", "还行", "一般"],
    "4. 米饭质量": ["好吃","偏硬", "偏烂" ],
    "5. 菜式变化": ["款式多变", "变化不多", "一成不变"],
    "6. 肉菜搭配": ["搭配合理", "肉太少", "青菜太少", "搭配不合理"],
    "7. 菜品口味": ["美味可口", "偏油", "偏咸", "有时未煮熟"],
    "8. 整体感觉": ["环境舒适整洁、饭菜可口", "环境一般、饭菜可口", "环境一般、饭菜一般", "环境差、饭菜口味差"],
    "9. 最关注的问题": ["饭堂的环境", "工作人员服务态度", "菜式搭配", "饭堂的餐具卫生"],
    "10. 满意度评分": ["100~90分", "90~80分", "80~70分", "70~60分", "60分以下"]
}

# ========== 管理员入口 完整数据+所有投票结果 ==========
if st.query_params.get("admin") == "888":
    st.subheader("📊 后台统计 & 全部答卷")
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file, encoding="utf-8-sig")
        st.info(f"总答卷数：{len(df)} 份")
        st.divider()
        # 每题投票统计
        st.subheader("一、各题目投票统计")
        for qname in questions_config.keys():
            if qname in df.columns:
                st.write(f"**{qname}**")
                st.dataframe(df[qname].value_counts(), use_container_width=True)
                st.divider()
        # 全部答卷明细（含第11题文字）
        st.subheader("二、全部答卷明细（含文字留言）")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("暂无调查数据")
    st.stop()

# ========== 普通用户投票页面 ==========
has_voted = cookies.get("has_voted") == "true"
if has_voted:
    st.success("✅ 您已完成本次调查，每人仅限提交一次！")
else:
    # 实时票数统计
    def get_count_data():
        res = {k:{o:0 for o in opts} for k,opts in questions_config.items()}
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file, encoding="utf-8-sig")
            for q in questions_config:
                if q in df.columns:
                    cnt = df[q].value_counts()
                    for k,v in cnt.items():
                        if k in res[q]:
                            res[q][k] = v
        return res

    count_data = get_count_data()

    with st.form("survey_form", clear_on_submit=False):
        q1 = st.radio("1. 饭菜新鲜度",
            [f"{x}（{count_data['1. 饭菜新鲜度'][x]}人）" for x in questions_config["1. 饭菜新鲜度"]],
            index=None, horizontal=True)

        q2 = st.radio("2. 异物发现情况",
            [f"{x}（{count_data['2. 异物发现情况'][x]}人）" for x in questions_config["2. 异物发现情况"]],
            index=None, horizontal=True)

        q3 = st.radio("3. 汤味道",
            [f"{x}（{count_data['3. 汤味道'][x]}人）" for x in questions_config["3. 汤味道"]],
            index=None, horizontal=True)

        q4 = st.radio("4. 米饭质量",
            [f"{x}（{count_data['4. 米饭质量'][x]}人）" for x in questions_config["4. 米饭质量"]],
            index=None, horizontal=True)

        q5 = st.radio("5. 菜式变化",
            [f"{x}（{count_data['5. 菜式变化'][x]}人）" for x in questions_config["5. 菜式变化"]],
            index=None, horizontal=True)

        q6 = st.radio("6. 肉菜搭配",
            [f"{x}（{count_data['6. 肉菜搭配'][x]}人）" for x in questions_config["6. 肉菜搭配"]],
            index=None, horizontal=True)

        q7 = st.radio("7. 菜品口味",
            [f"{x}（{count_data['7. 菜品口味'][x]}人）" for x in questions_config["7. 菜品口味"]],
            index=None, horizontal=True)

        q8 = st.radio("8. 整体感觉",
            [f"{x}（{count_data['8. 整体感觉'][x]}人）" for x in questions_config["8. 整体感觉"]],
            index=None)

        q9 = st.radio("9. 最关注的问题",
            [f"{x}（{count_data['9. 最关注的问题'][x]}人）" for x in questions_config["9. 最关注的问题"]],
            index=None, horizontal=True)

        q10 = st.radio("10. 满意度评分",
            [f"{x}（{count_data['10. 满意度评分'][x]}人）" for x in questions_config["10. 满意度评分"]],
            index=None, horizontal=True)

        st.divider()
        q11 = st.text_area("11. 请写出您喜欢或不喜欢的菜品", height=80, placeholder="例如：喜欢炸鸡腿")
        submit_btn = st.form_submit_button("提交", type="primary", use_container_width=True)

        if submit_btn:
            def trim_name(s):
                return s.split("（")[0] if s else None

            check_list = [q1,q2,q3,q4,q5,q6,q7,q8,q9,q10]
            if not all(check_list):
                st.error("⚠️ 请完成全部选择题再提交！")
            else:
                row = {
                    "提交时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "1. 饭菜新鲜度": trim_name(q1),
                    "2. 异物发现情况": trim_name(q2),
                    "3. 汤味道": trim_name(q3),
                    "4. 米饭质量": trim_name(q4),
                    "5. 菜式变化": trim_name(q5),
                    "6. 肉菜搭配": trim_name(q6),
                    "7. 菜品口味": trim_name(q7),
                    "8. 整体感觉": trim_name(q8),
                    "9. 最关注的问题": trim_name(q9),
                    "10. 满意度评分": trim_name(q10),
                    "11. 文字建议": q11.strip() if q11 else "无"
                }
                df_new = pd.DataFrame([row])
                if os.path.exists(csv_file):
                    df_new.to_csv(csv_file, mode="a", header=False, index=False, encoding="utf-8-sig")
                else:
                    df_new.to_csv(csv_file, index=False, encoding="utf-8-sig")
                # 标记已投票
                cookies["has_voted"] = "true"
                cookies.save()
                st.success("提交成功，感谢您的反馈！")
                st.balloons()
