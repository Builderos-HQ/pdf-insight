import streamlit as st
import fitz
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


# ==========================================
# Configuration
# ==========================================

load_dotenv()

client = OpenAI()


# ==========================================
# AI response structures
# ==========================================

class ScoreReason(BaseModel):
    points: int
    reason: str


class SkillMatch(BaseModel):
    skill: str
    matched: bool
    comment: str


class JobAnalysis(BaseModel):
    score: int
    decision: str
    score_reasons: list[ScoreReason]
    summary: list[str]
    conditions: list[str]
    warnings: list[str]
    next_actions: list[str]
    match_score: int
    match_summary: str
    skill_matches: list[SkillMatch]
    application_message: str


# ==========================================
# Page configuration
# ==========================================

st.set_page_config(
    page_title="PDF Insight",
    page_icon="📄",
    layout="wide"
)


# ==========================================
# Header
# ==========================================

st.title("📄 PDF Insight")

st.write(
    "AIでフリーランス案件を分析し、"
    "応募すべき案件を判断します。"
)


# ==========================================
# Sidebar
# ==========================================

with st.sidebar:

    st.header("👤 あなたについて")

    user_skills = st.text_area(
        "スキル",
        placeholder=(
            "Python\n"
            "Streamlit\n"
            "OpenAI API\n"
            "GitHub\n"
            "Web開発"
        ),
        height=180
    )

    st.caption(
        "案件とのスキル適合度の判定に使用します。"
    )


# ==========================================
# Upload
# ==========================================

st.subheader("📄 案件PDF")

uploaded_file = st.file_uploader(
    "案件PDFをアップロード",
    type=["pdf"]
)


# ==========================================
# Main process
# ==========================================

if uploaded_file is not None:

    st.success(
        f"✓ {uploaded_file.name}"
    )

    pdf = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in pdf:
        text += page.get_text()


    st.caption(
        f"{len(pdf)}ページのPDFを読み込みました。"
    )


    # ======================================
    # Analyze
    # ======================================

    if st.button(
        "🤖 AIで分析する",
        type="primary",
        use_container_width=True
    ):

        if not user_skills.strip():

            st.warning(
                "左側の「あなたについて」に"
                "スキルを入力してください。"
            )

            st.stop()


        with st.spinner(
            "AIが案件を分析しています..."
        ):

            response = client.responses.parse(

                model="gpt-5",

                input=f"""
あなたはフリーランス案件の
AIスクリーニングアシスタントです。

以下の案件PDFを分析してください。

日本語で回答してください。


================================
案件おすすめ度
================================

score:

応募おすすめ度を1〜10で評価。


================================
応募判断
================================

decision:

以下から1つ：

- 応募する
- 検討する
- 応募しない


================================
評価理由
================================

score_reasons:

おすすめ度の理由。

良い点はプラス、
悪い点はマイナス。


================================
重要ポイント
================================

summary:

重要な内容を3〜5個。


================================
案件条件
================================

conditions:

- 報酬
- 納期
- 必要スキル
- 作業内容
- 応募条件


================================
注意点
================================

warnings:

リスクや注意点。


================================
次にやること
================================

next_actions:

次にやるべきことを3つ以内。


================================
あなたとの相性
================================

ユーザーのスキル：

{user_skills}


match_score:

ユーザーと案件の適合度を
0〜100で評価。


match_summary:

適合度について説明。


skill_matches:

案件の重要スキルについて、

skill:
スキル名

matched:
ユーザーが持っていればtrue、
持っていなければfalse

comment:
理由


================================
応募文
================================

application_message:

案件に応募するための
自然で簡潔な応募文。

ユーザーのスキルを反映。

経験について嘘を書かない。

日本語で作成。


================================
PDF
================================

{text}
""",

                text_format=JobAnalysis,
            )

            analysis = response.output_parsed


        # ==================================
        # RESULT
        # ==================================

        st.divider()

        st.header("📊 分析結果")


        # ==================================
        # Top result
        # ==================================

        if analysis.decision == "応募する":

            st.success(
                "🟢 この案件は応募がおすすめです"
            )

        elif analysis.decision == "検討する":

            st.warning(
                "🟡 この案件は検討する価値があります"
            )

        else:

            st.error(
                "🔴 この案件はおすすめしません"
            )


        # ==================================
        # Score columns
        # ==================================

        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "⭐ おすすめ度",
                f"{analysis.score} / 10"
            )

            st.progress(
                analysis.score / 10
            )


        with col2:

            st.metric(
                "🎯 あなたとの相性",
                f"{analysis.match_score}%"
            )

            st.progress(
                analysis.match_score / 100
            )


        # ==================================
        # Score reasons
        # ==================================

        st.divider()

        st.subheader("💡 なぜこの評価？")

        for item in analysis.score_reasons:

            if item.points > 0:

                st.write(
                    f"🟢 +{item.points}  "
                    f"{item.reason}"
                )

            else:

                st.write(
                    f"🔴 {item.points}  "
                    f"{item.reason}"
                )


        # ==================================
        # Skill match
        # ==================================

        st.divider()

        st.subheader("🧩 スキル照合")

        for item in analysis.skill_matches:

            if item.matched:

                st.success(
                    f"✓ {item.skill} — "
                    f"{item.comment}"
                )

            else:

                st.warning(
                    f"⚠️ {item.skill} — "
                    f"{item.comment}"
                )


        # ==================================
        # Summary
        # ==================================

        st.divider()

        st.subheader("📌 重要ポイント")

        for item in analysis.summary:

            st.write(
                f"• {item}"
            )


        # ==================================
        # Conditions / warnings
        # ==================================

        st.divider()

        col1, col2 = st.columns(2)


        with col1:

            st.subheader("💼 案件条件")

            for item in analysis.conditions:

                st.write(
                    f"• {item}"
                )


        with col2:

            st.subheader("⚠️ 注意点")

            for item in analysis.warnings:

                st.write(
                    f"• {item}"
                )


        # ==================================
        # Next actions
        # ==================================

        st.divider()

        st.subheader("🚀 次にやること")

        for i, item in enumerate(
            analysis.next_actions,
            start=1
        ):

            st.write(
                f"**{i}.** {item}"
            )


        # ==================================
        # Application
        # ==================================

        st.divider()

        st.header("✍️ AI応募文")

        st.text_area(
            "応募文を確認・編集してください",
            value=analysis.application_message,
            height=300
        )

        st.info(
            "💡 応募前に必ず内容を確認し、"
            "自分の経験に合わせて編集してください。"
        )


else:

    st.info(
        "👆 案件PDFをアップロードして"
        "AI分析を始めましょう。"
    )
    