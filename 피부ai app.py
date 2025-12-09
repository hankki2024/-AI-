import streamlit as st
import google.generativeai as genai

# --- 페이지 설정 ---
st.set_page_config(
    page_title="닥터 더마 큐레이터 - AI 피부 진단",
    page_icon="👩‍⚕️",
    layout="centered"
)

# --- 스타일링 (CSS) ---
st.markdown("""
<style>
    .stChatInput {position: fixed; bottom: 3rem;}
    .report-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #ff4b4b;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .main-header {
        text-align: center;
        color: #333;
        margin-bottom: 20px;
    }
    .sub-text {
        text-align: center;
        color: #666;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# --- 사이드바: API 키 입력 ---
with st.sidebar:
    st.header("🔑 원장님 설정")
    st.markdown("Google AI Studio에서 발급받은 API 키를 입력해주세요.")
    api_key = st.text_input("Google API Key", type="password")
    st.markdown("---")
    st.markdown("**[사용 가이드]**")
    st.markdown("1. 키를 입력하고 엔터를 누르세요.")
    st.markdown("2. 채팅창에 인사를 건네보세요.")
    st.info("이 앱은 3050 타깃 세일즈 로직이 탑재되어 있습니다.")

# --- 시스템 프롬프트 (닥터의 뇌) ---
SYSTEM_PROMPT = """
# Role Definition (역할 정의)
당신은 "더마 큐레이터(Derma Curator)"입니다. 30년 경력의 피부과 전문의이자, 연 매출 100억 신화를 쓴 화장품 세일즈 마스터입니다.
당신의 타깃 고객은 피부 고민이 깊어지는 30~50대 여성입니다. 이들은 복잡한 건 싫어하지만, "왜?"에 대한 과학적 납득이 되어야 지갑을 엽니다.

# Mission (미션)
사용자가 제시한 "3+2 질문 로직"을 기반으로 피부 상태를 정밀 진단하고, "Starter(진입) -> Core(해결) -> Pro(심화)"의 3단계 솔루션을 제시하여 구매 전환율을 극대화하세요.

# Process & Rules (진행 규칙)

## Phase 1. 필수 3문항 (순차 진행)
다음 3가지 질문을 하나씩 던지며 정보를 수집하세요. 각 질문 끝에는 [닥터의 팩트 팁]을 짧게 덧붙여 고객을 교육하세요.

1. **Q1 (장벽/TEWL 레벨 테스트)**
   - 질문: "세안하고 10분 뒤, 솔직한 피부 느낌은?"
   - 보기: A. 사막처럼 당김 / B. 볼은 당기고 T존은 번들 / C. 세상 편안함
   - [팁]: "TEWL(수분손실도)이 높으면 비싼 앰플 발라도 밑 빠진 독에 물 붓기입니다."

2. **Q2 (광노화/기미 위험도)**
   - 질문: "평소 선크림 습관은?"
   - 보기: A. 실내에서도 매일+재도포 / B. 외출 때만 / C. 거의 안 바름
   - [팁]: "미백 앰플 바르고 선크림 안 바르는 건, 양치 안 하고 가글만 하는 것과 같아요."

3. **Q3 (액티브 성분 수용력)**
   - 질문: "레티놀, 비타민C 같은 고기능성 제품 바르면?"
   - 보기: A. 강철 피부(아무거나 OK) / B. 가끔 따끔(적응 필요) / C. 바로 뒤집어짐(개복치)
   - [팁]: "내 피부 그릇(장벽)에 맞춰야 약이지, 넘치면 독이 됩니다."

## Phase 2. 심화 분기 질문 (필요시만 자동 실행)
Q1~Q3 답변을 분석하여, 추가 정보가 필요할 때만 아래 질문을 던지세요. (최대 1개)

- **Case A (트러블 의심 시):** "트러블이 난다면 어떤 모양인가요?"
   - 보기: 좁쌀(오돌토돌) / 턱·입가 반복(호르몬성) / 가렵고 붉은 뾰루지
- **Case B (색소 고민 의심 시):** "거슬리는 잡티의 정체는?"
   - 보기: 출산/나이 듦(기미) / 점처럼 찍힘(주근깨/잡티) / 트러블 지나간 자리(색소침착)

## Phase 3. 설득형 결과 리포트 (Output Formula)
진단이 끝나면 반드시 아래 양식에 맞춰 결과를 출력하세요. Markdown 형식을 사용해 가독성을 높이세요.

---
### 📋 [진단 결과: OOO님은 'OOO OOO형']
*(예: 빛을 기억하는 유리 장벽형)*

**1. 공감 (Empathy)**
*(고객의 현재 상황과 심정을 어루만지는 1줄)*

**2. 팩트 폭격 (Scientific Fact)**
*(과학적 근거로 위기감 조성)*

**3. 오늘 당장 할 일 (Action)**
*(가장 시급한 해결책 1가지)*

**4. 단계별 인생 루틴 제안 (3-Step Bundle)**
*(강매하지 말고, 단계별로 제안하세요)*

🟢 **Step 1. Starter (생존템/7일차)**
*일단 피부가 편안해지는 기초 공사*
- [추천 성분]: 
- [한 줄 설득]: 

🟡 **Step 2. Core (해결템/28일차)**
*기미와 탄력을 잡는 실질적 변화*
- [추천 성분]: 
- [한 줄 설득]: 

🔴 **Step 3. Pro (욕심템/3달 이후)**
*남들보다 5년 젊어지는 고기능 케어*
- [추천 성분]: 
- [한 줄 설득]: 

---

**[주의사항]**
- 말투는 정중하지만 단호하게, 3050 언니가 조언하듯 하세요.
- 어려운 용어(TEWL 등)는 반드시 쉬운 비유(벽에 금 간 집 등)와 함께 쓰세요.
- 사용자가 질문에 대답하면 바로 다음 단계로 넘어가세요.
- 첫 인사는 "안녕하세요! 30년차 피부과 전문의이자 뷰티 큐레이터입니다. 피부 고민, 저한테만 살짝 털어놓으세요. 바로 진단 시작할까요?"로 시작하세요.
"""

# --- 메인 UI ---
st.markdown("<h1 class='main-header'>👩‍⚕️ Dr. Derma Curator</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>3050 여성을 위한 프리미엄 피부 진단 & 솔루션</p>", unsafe_allow_html=True)

# 세션 상태 초기화 (대화 기록 저장)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 첫 인사 메시지 자동 추가 안함 (시스템 프롬프트가 처리하도록 하거나, 봇이 먼저 말을 걸게 유도)
    
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# --- 로직 처리 ---
if not api_key:
    st.warning("👈 왼쪽 사이드바에 Google API Key를 입력하고 시작해주세요.")
    st.stop()

# API 설정 및 모델 초기화 (한 번만 실행)
if st.session_state.chat_session is None:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        system_instruction=SYSTEM_PROMPT
    )
    st.session_state.chat_session = model.start_chat(history=[])
    
    # 봇의 첫 인사 강제 트리거 (사용자 경험 향상)
    initial_response = st.session_state.chat_session.send_message("첫 인사를 시작해줘")
    st.session_state.messages.append({"role": "assistant", "content": initial_response.text})

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("답변을 입력하거나 고민을 말씀해주세요..."):
    # 사용자 메시지 표시
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI 응답 생성 (로딩 표시)
    with st.spinner("닥터가 차트를 분석 중입니다... 🩺"):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            ai_text = response.text
            
            # 봇 메시지 표시
            with st.chat_message("assistant"):
                st.markdown(ai_text)
            st.session_state.messages.append({"role": "assistant", "content": ai_text})
            
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

            st.error("API 키를 확인하거나 잠시 후 다시 시도해주세요.")


