import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
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
# 2. 核心数据分析函数 (科研通道专用 - 纯英文双图看板)
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
        
        # 简单可视化：双图联动科研分析面板 (完全英文版，防止乱码)
        st.markdown("#### 🔍 Multi-Dimensional Scientific Analysis")
        try:
            # 1. 数据准备与英文映射
            plot_df = df.copy()
            type_mapping = {
                "步行/骑行 (主动通勤)": "Active (Walk/Bike)",
                "地铁 (Subway)": "Subway",
                "公交 (Bus)": "Bus",
                "自驾 (Driving)": "Driving",
                "打车/拼车 (Ride-hailing)": "Ride-hailing"
            }
            plot_df["commute_type_en"] = plot_df["commute_type"].map(type_mapping).fillna(plot_df["commute_type"])
            
            # 统一设置 Arial 字体，防止乱码
            plt.rcParams['font.sans-serif'] = ['Arial', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 2. 创建 1行2列 的画布
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # --- 【左图】散点趋势图：通勤时间与压力的相关性 ---
            ax1.scatter(plot_df["commute_time"], plot_df["stress_score"], color='#2980B9', alpha=0.7, edgecolors='none', s=80)
            
            # 尝试绘制趋势线（线性拟合）
            m = 0 # 默认斜率
            if len(plot_df) >= 2:
                m, b = np.polyfit(plot_df["commute_time"].astype(float), plot_df["stress_score"].astype(float), 1)
                ax1.plot(plot_df["commute_time"], m*plot_df["commute_time"] + b, color='#E74C3C', linestyle='--', linewidth=2, label=f'Trend (slope: {m:.2f})')
                ax1.legend()
                
            ax1.set_title("Correlation: Commute Time vs. Stress", fontsize=11, fontweight='bold', pad=10)
            ax1.set_xlabel("Commute Duration (Minutes)", fontsize=9)
            ax1.set_ylabel("Morning Stress Score (3-15)", fontsize=9)
            ax1.set_ylim(2, 16)
            ax1.grid(True, linestyle=':', alpha=0.6)
            
            # --- 【右图】双柱对比图：不同通勤方式的[拥挤度]与[压力值] ---
            grouped = plot_df.groupby("commute_type_en")[["crowd_level", "stress_score"]].mean().reset_index()
            
            # 柱状图排版参数
            x_indices = np.arange(len(grouped))
            width = 0.35
            
            # 绘制双柱（压力除以3以便在同一维度对比）
            ax2.bar(x_indices - width/2, grouped["crowd_level"], width, label='Avg Crowdedness (1-5)', color='#F39C12')
            ax2.bar(x_indices + width/2, grouped["stress_score"] / 3, width, label='Normalized Stress (Score/3)', color='#27AE60')
            
            ax2.set_title("Impact: Crowdedness vs. Normalized Stress", fontsize=11, fontweight='bold', pad=10)
            ax2.set_xlabel("Commute Type", fontsize=9)
            ax2.set_ylabel("Level / Normalized Score", fontsize=9)
            ax2.set_xticks(x_indices)
            ax2.set_xticklabels(grouped["commute_type_en"], rotation=15, ha='right', fontsize=8)
            ax2.set_ylim(0, 6)
            ax2.legend()
            ax2.grid(True, linestyle=':', alpha=0.6)
            
            # 调整布局并渲染
            plt.tight_layout()
            st.pyplot(fig)
            
            # 3. 补充学术结论输出（动态文字分析）
            st.markdown("#### 💡 Key Research Insights:")
            col_left, col_right = st.columns(2)
            with col_left:
                if len(plot_df) >= 2 and m > 0:
                    st.write(f"📈 **Time Factor**: Commute duration is **positively correlated** with morning stress. Every additional 10 minutes of commuting increases stress by approximately **{m*10:.2f}** points.")
                else:
                    st.write("📈 **Time Factor**: Awaiting more data points to calculate the exact correlation coefficient.")
            with col_right:
                high_crowd = grouped[grouped["crowd_level"] >= 3.5]
                if not high_crowd.empty:
                    types = ", ".join(high_crowd["commute_type_en"].tolist())
                    st.write(f"⚠️ **Crowd Factor**: High crowdedness (>=3.5) detected in **{types}**. Crowded environments significantly drain morning psychological energy.")
                else:
                    st.write("⚠️ **Crowd Factor**: Crowdedness levels are currently stable across all commute types.")
                    
        except Exception as e:
            st.error(f"Chart rendering failed: {e}")
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
        
    # --- 通勤压力感知单选按钮 ---
    st.write("") 
    st.markdown("""
        <p style="margin-bottom: 5px; font-weight: bold; font-size: 16px;">
            🚦 通勤过程中的拥挤/路况压力感知 (单选)
        </p>
        <p style="margin-bottom: 15px; font-size: 14px; color: #566573;">
            💡 评分标准：<strong>1分</strong>（非常通畅/有座位，非常舒适） ↔️ <strong>5分</strong>（非常拥堵/无座位，非常烦躁）
        </p>
    """, unsafe_allow_html=True)
    
    crowd_level = st.radio(
        label="请选择您的压力感知分数：",
        options=[1, 2, 3, 4, 5],
        index=2,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.write("") 
    
    sleep_hours = st.slider("昨晚睡眠时长 (小时)", min_value=4.0, max_value=10.0, value=7.0, step=0.5,
                            help="睡眠是重要的心理缓冲因子")

    st.markdown("---")

    # --- 第二板块：K10 晨间即时压力自评 ---
    st.subheader("2. 当前心理状态自评 (K10 简版)")
    
    st.markdown("""
        <div style="background-color: #F8F9F9; border-left: 4px solid #5D6D7E; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
            <p style="margin: 0 0 8px 0; font-weight: bold; color: #2C3E50; font-size: 15px;">
                📝 评分标准说明（请根据此时此刻抵达工位后的真实感受选择）：
            </p>
            <div style="display: flex; justify-content: space-between; font-size: 13px; color: #566573; max-width: 500px;">
                <span><strong>1分</strong>：极轻 / 完全没有</span>
                <span><strong>2分</strong>：轻度</span>
                <span><strong>3分</strong>：中度</span>
                <span><strong>4分</strong>：重度</span>
                <span><strong>5分</strong>：极重 / 非常强烈</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='font-weight: bold; margin-bottom: 5px;'>1. 您现在感到紧张或焦虑吗？</p>", unsafe_allow_html=True)
    stress_q1 = st.radio(
        label="q1",
        options=[1, 2, 3, 4, 5],
        index=2,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.write("") 
    
    st.markdown("<p style='font-weight: bold; margin-bottom: 5px;'>2. 您现在感到疲惫、没有活力吗？</p>", unsafe_allow_html=True)
    stress_q2 = st.radio(
        label="q2",
        options=[1, 2, 3, 4, 5],
        index=2,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.write("") 
    
    st.markdown("<p style='font-weight: bold; margin-bottom: 5px;'>3. 您现在感到烦躁、难以平静吗？</p>", unsafe_allow_html=True)
    stress_q3 = st.radio(
        label="q3",
        options=[1, 2, 3, 4, 5],
        index=2,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    total_stress_score = stress_q1 + stress_q2 + stress_q3

    # --- 第三板块：动态能量天平反馈 ---
    st.markdown("---")
    st.subheader("⚖️ 您的晨间心理能量天平")
    
    stress_load = (commute_time / 10) + (crowd_level * 2)
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
