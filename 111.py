import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================
# 1. 页面基本配置与初始化
# ==========================================
st.set_page_config(page_title="城市通勤与晨间压力研究", layout="centered", page_icon="🚗")

# 初始化路由状态
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "show_admin_portal" not in st.session_state:
    st.session_state.show_admin_portal = False

# 初始化 CSV 数据库
DB_FILE = "commute_history.csv"
def init_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=[
            "timestamp", "gender", "age", "commute_type", 
            "commute_time", "crowd_level", "sleep_hours", "stress_score"
        ])
        df.to_csv(DB_FILE, index=False)

init_db()

# ==========================================
# 2. 核心数据分析函数 (科研通道专用)
# ==========================================
def show_admin_trend_analysis():
    st.markdown("### 📊 实验室实时科研数据看板")
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        if len(df) == 0:
            st.info("目前后台暂无样本数据，快去提交几份测试数据吧！")
            return
        
        st.write(f"📊 **当前已收集有效样本数**：{len(df)} 份")
        
        # 展示最近 5 条数据
        st.dataframe(df.tail(5), use_container_width=True)
        
        # 简单可视化：不同通勤方式的平均压力
        st.markdown("#### 🔍 不同通勤方式的平均压力分布")
        try:
            avg_stress = df.groupby("commute_type")["stress_score"].mean().reset_index()
            
            # 绘制柱状图
            fig, ax = plt.subplots(figsize=(8, 4))
            # 支持中文显示
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            
            colors = ['#2980B9', '#27AE60', '#E74C3C', '#F39C12', '#9B59B6']
            ax.bar(avg_stress["commute_type"], avg_stress["stress_score"], color=colors[:len(avg_stress)])
            ax.set_ylabel("平均晨间压力值 (3-15分)")
            ax.set_xlabel("通勤方式")
            ax.set_ylim(0, 15)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"图表渲染失败: {e}")
    else:
        st.error("未找到数据库文件。")

# ==========================================
# 3. 路由渲染逻辑
# ==========================================

# ------------------------------------------
# 路线 A：Landing Page (欢迎与知情同意页)
# ------------------------------------------
if not st.session_state.confirmed:
    st.title("🚗 城市通勤与晨间压力微评估")
    st.markdown("""
    ### 🔬 欢迎参与大数据实验室学术研究
    这是一项关于**城市通勤特征与上班族晨间即时心理压力**的微型实证研究。
    
    *   **评估时间**：约 30 秒。
    *   **隐私保护**：本研究严格遵守学术伦理，所有数据均进行**完全匿名化**处理，不收集任何个人身份信息（PII）。
    *   **研究价值**：您的数据将帮助我们探索通勤时间、拥挤度对打工人心理能量的损耗边界。
    """)
    
    st.info("💡 提示：请在您刚刚到达工位、或准备开始工作时填写本评估，以保证数据的即时性。")
    
    if st.button("开始评估 (Start Evaluation)", use_container_width=True):
        st.session_state.confirmed = True
        st.rerun()

# ------------------------------------------
# 路线 B：Main Dashboard (正式评估页)
# ------------------------------------------
else:
    st.title("📝 晨间压力与通勤特征登记")
    st.write("请根据您**今天早上**的实际通勤情况和**当前**的心理感受进行填写。")
    
    # --- 第一板块：基本信息与通勤特征 ---
    st.subheader("1. 通勤特征登记")
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("您的性别 (Gender)", ["男 (Male)", "女 (Female)", "其他 (Other)"])
        age = st.number_input("您的年龄 (Age)", min_value=18, max_value=70, value=25)
    with col2:
        commute_type = st.selectbox(
            "今天早上的主要通勤方式 (Commute Type)",
            ["步行/骑行 (主动通勤)", "地铁 (Subway)", "公交 (Bus)", "自驾 (Driving)", "打车/拼车 (Ride-hailing)"]
        )
        commute_time = st.slider("单程通勤时长 (分钟)", min_value=5, max_value=120, value=30, step=5)
        
    crowd_level = st.slider("通勤过程中的拥挤/路况压力感知", min_value=1, max_value=5, value=3, 
                            help="1分：一路畅通/有座，非常舒适；5分：极度拥堵/挤成沙丁鱼，非常烦躁")
    
    sleep_hours = st.slider("昨晚睡眠时长 (小时)", min_value=4.0, max_value=10.0, value=7.0, step=0.5,
                            help="睡眠是重要的心理缓冲因子")

    st.markdown("---")

    # --- 第二板块：K10 晨间即时压力自评 ---
    st.subheader("2. 当前心理状态自评 (K10 简版)")
    st.write("请评估您**此时此刻（刚刚抵达工位）**的真实感受：")
    
    stress_q1 = st.radio("1. 您现在感到紧张或焦虑吗？", [1, 2, 3, 4, 5], horizontal=True, 
                         format_func=lambda x: f"{x}分 (极轻 -> 极重)")
    stress_q2 = st.radio("2. 您现在感到疲惫、没有活力吗？", [1, 2, 3, 4, 5], horizontal=True,
                         format_func=lambda x: f"{x}分 (极轻 -> 极重)")
    stress_q3 = st.radio("3. 您现在感到烦躁、难以平静吗？", [1, 2, 3, 4, 5], horizontal=True,
                         format_func=lambda x: f"{x}分 (极轻 -> 极重)")
    
    # 计算总分 (3 - 15 分)
    total_stress_score = stress_q1 + stress_q2 + stress_q3

    # --- 第三板块：动态能量天平反馈 ---
    st.markdown("---")
    st.subheader("⚖️ 您的晨间心理能量天平")
    
    # 简单的天平逻辑计算
    # 压力源 = 通勤时间权重 + 拥挤度权重
    stress_load = (commute_time / 10) + (crowd_level * 2)
    # 缓冲器 = 睡眠时间权重 + 主动通勤加成
    buffer_power = (sleep_hours * 1.5) + (3 if "步行/骑行" in commute_type else 0)
    
    balance_diff = stress_load - buffer_power
    
    if balance_diff > 3:
        st.error(f"⚖️ **天平严重向【压力源】倾斜** (净超载值: {balance_diff:.1f})")
        st.write("诊断建议：今晨的通勤消耗了您过多的心理能量。建议在开始高强度工作前，进行 5 分钟的深呼吸或闭眼冥想，主动为大脑“降温”。")
    elif balance_diff < -3:
        st.success(f"⚖️ **天平向【心理缓冲】倾斜** (净储备值: {abs(balance_diff):.1f})")
        st.write("诊断建议：充足的睡眠或轻松的通勤为您注入了满满的晨间活力！今天非常适合处理富有创造力和挑战性的工作。")
    else:
        st.info(f"⚖️ **天平基本保持平衡** (波动值: {balance_diff:.1f})")
        st.write("诊断建议：您的心理能量处于平稳状态。保持节奏，开启高效的一天吧！")

    # --- 提交数据 ---
    if st.button("提交评估并记录数据 (Submit)", use_container_width=True):
        # 保存数据到 CSV
        df = pd.read_csv(DB_FILE)
        new_data = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gender": gender,
            "age": age,
            "commute_type": commute_type,
            "commute_time": commute_time,
            "crowd_level": crowd_level,
            "sleep_hours": sleep_hours,
            "stress_score": total_stress_score
        }])
        new_data.to_csv(DB_FILE, mode='a', header=False, index=False)
        st.balloons()
        st.success("数据提交成功！感谢您为城市打工人心理健康研究做出的贡献。")

    # ==========================================
    # 🔐 4. 管理员后台密码验证与渲染 (科技蓝一体化设计)
    # ==========================================
    st.markdown("---")
    
    # 注入精准的科技蓝按钮与仅限验证框的 CSS
    st.markdown("""
        <style>
        div:has(#blue-btn-marker) + div button {
            background-color: #2980B9 !important;
            color: white !important;
            border: 1px solid #2980B9 !important;
            font-weight: bold !important;
            padding: 12px 24px !important;
            border-radius: 10px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(41, 128, 185, 0.2) !important;
        }
        div:has(#blue-btn-marker) + div button:hover {
            background-color: #1F618D !important;
            border-color: #1F618D !important;
            box-shadow: 0 6px 15px rgba(41, 128, 185, 0.4) !important;
            transform: translateY(-1px);
        }
        div:has(#blue-btn-marker) ~ div[data-testid="stVerticalBlock"]:has(.blue-login-inside) {
            background-color: #F0F4F8 !important;
            border: 2px solid #2980B9 !important;
            border-radius: 12px !important;
            padding: 25px !important;
            margin-top: 20px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div id="blue-btn-marker"></div>', unsafe_allow_html=True)
    btn_label = "🔒 关闭科研通道 (Close Portal)" if st.session_state.show_admin_portal else "🔑 大数据实验室科研人员通道 (Research Portal)"
    
    if st.button(btn_label, key="btn_admin_toggle", use_container_width=True):
        st.session_state.show_admin_portal = not st.session_state.show_admin_portal
        st.rerun()

    if st.session_state.show_admin_portal:
        with st.container():
            st.markdown('<div class="blue-login-inside"></div>', unsafe_allow_html=True)
            st.markdown("""
                <h4 style="margin: 0 0 10px 0; color: #1F618D; font-size: 18px; font-weight: bold;">
                    🔒 安全验证 (Security Verification)
                </h4>
                <p style="margin: 0 0 20px 0; font-size: 14px; color: #566573;">
                    该区域仅对实验室授权研究人员开放，请输入密码以加载宏观数据分析面板。
                </p>
            """, unsafe_allow_html=True)
            
            admin_password = st.text_input(
                "请输入实验室授权密码 (Enter Password)", 
                type="password", 
                key="admin_pwd"
            )
        
        if admin_password == "admin123":
            st.write("")
            st.success("密码正确！已成功载入大数据分析面板。")
            st.write("")
            show_admin_trend_analysis()
        elif admin_password != "":
            st.error("密码错误，拒绝访问。")
