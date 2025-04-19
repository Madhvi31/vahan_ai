import streamlit as st
import wikipedia
import datetime
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
from scholarly import scholarly
import cohere

# --- API Keys ---
COHERE_API_KEY = st.secrets["api_keys"]["cohere"]
YOUTUBE_API_KEY = st.secrets["api_keys"]["youtube"]

co = cohere.Client(COHERE_API_KEY)

# --- PAGE CONFIG ---
st.set_page_config(page_title="AI Learning Assistant", layout="wide")

# --- CSS STYLING ---
def load_css():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://static.vecteezy.com/system/resources/previews/003/641/130/original/colorful-pink-blurred-backgrounds-valentine-s-day-pink-background-abstract-gradient-light-pink-illustration-free-vector.jpg");
            background-color: #f8f8f8;
            background-repeat: no-repeat;
            background-size: cover;
            background-position: center;
            color: black;
        }

        section[data-testid="stSidebar"] {
            background-color: #fdfdfd !important;
            color: black !important;
            border-right: 1px solid #ddd;
        }

        .main .block-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            color: black !important;
        }

        h1, h2, h3, h4, h5, h6, p, li, span, label, div {
            color: black !important;
        }

        input, textarea, select {
            background-color: #fff !important;
            color: black !important;
            border: 1px solid #ccc !important;
        }
        input::placeholder, textarea::placeholder {
            color: #666 !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #fff !important;
            color: black !important;
        }

        .stButton>button, section[data-testid="stDownloadButton"] button {
            background-color: #FFD700 !important;
            color: red !important;
            font-weight: bold;
            border-radius: 8px;
            border: 1px solid red;
        }

        .stButton>button:hover, section[data-testid="stDownloadButton"] button:hover {
            background-color: #FFC300 !important;
            transform: scale(1.02);
        }

        .stTextInput, .stTextArea, .stSelectbox {
            margin-bottom: 1rem;
        }

        .stExpander {
            background-color: #fdfdfd !important;
            border: 1px solid #ccc !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

load_css()

# --- Memory ---
if "memory" not in st.session_state:
    st.session_state.memory = {}

# --- Data Sources ---
def fetch_from_web(topic):
    try:
        summary = wikipedia.summary(topic, sentences=10)
        source = wikipedia.page(topic).url
        return summary, source
    except:
        return f"No web content found for {topic}.", "https://en.wikipedia.org/"

def fetch_from_video(topic):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            part="snippet",
            q=topic,
            type="video",
            maxResults=1,
            videoEmbeddable="true"
        )
        response = request.execute()
        if response["items"]:
            video_id = response["items"][0]["id"]["videoId"]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            title = response["items"][0]["snippet"]["title"]
            transcript = f"This video titled '{title}' provides an introduction to {topic} using real-world examples and visuals."
            return transcript, embed_url
        else:
            return "No relevant videos found.", ""
    except Exception as e:
        return f"Error fetching video: {str(e)}", ""

def fetch_real_academic_extract(topic):
    try:
        search_query = scholarly.search_pubs(topic)
        top_result = next(search_query)
        summary = top_result['bib']['title'] + " — " + top_result['bib'].get('abstract', 'No abstract available.')
        link = top_result.get('pub_url', f"https://scholar.google.com/scholar?q={topic}")
        return summary, link
    except:
        return "No academic extracts found.", f"https://scholar.google.com/scholar?q={topic}"

# --- Visual Flow ---
def plot_topic_flow(topic):
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.text(0.5, 0.8, topic, fontsize=12, ha='center', color='black')
    ax.text(0.5, 0.6, "\u2192 Understanding", fontsize=10, ha='center', color='black')
    ax.text(0.5, 0.4, "\u2192 Application", fontsize=10, ha='center', color='black')
    ax.text(0.5, 0.2, "\u2192 Evaluation", fontsize=10, ha='center', color='black')
    ax.set_facecolor('none')
    fig.patch.set_alpha(0)
    ax.axis("off")
    return fig

# --- Report Generator ---
def generate_report(topic, user_profile, research):
    date = datetime.date.today().strftime("%B %d, %Y")
    report = f"""
# Learning Report: {topic}
**Date:** {date}

## Clarifying Focus
{user_profile['clarifying_question']}

## Learning Objectives
{user_profile['learning_goal']}

## Learner Profile
- **Knowledge Level:** {user_profile['knowledge_level']}
- **Interest Focus:** {user_profile['interest_focus']}
- **Preferred Format:** {user_profile['preferred_format']}

## Web Content Summary
{research['web']['content']}

**Citation:** [{research['web']['source']}]({research['web']['source']})

## Video Resource
{research['video']['content']}

**Watch:** [{research['video']['source']}]({research['video']['source']})

## Academic Research
{research['academic']['content']}

**Read more:** [{research['academic']['source']}]({research['academic']['source']})

## Visual Concept Flow
A diagram representing the learning flow for this topic.

## Recommended Next Steps
1. Explore beginner-friendly resources on "{topic}"
2. Apply concepts through practical exercises
3. Dive deeper into specific areas of interest

*Report generated by the Enhanced Interactive Learning Assistant*
"""
    return report

# --- Sidebar ---
with st.sidebar:
    st.title("Learning Assistant")
    st.markdown("Create personalized learning reports on any topic.")
    st.markdown("---")
    st.markdown("""
        <div>
            <p><strong>Tips:</strong></p>
            <ul>
                <li>Be specific with your topic</li>
                <li>Provide detailed learning goals</li>
                <li>Select your knowledge level accurately</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# --- Main App ---
st.title("Enhanced Interactive Learning Assistant")
st.markdown("Create a personalized, AI-powered learning report from any topic.")

topic = st.text_input("Enter a learning topic:", placeholder="e.g. Neural Networks, Quantum Computing")
clarifying_q = st.text_input("What part of this topic are you most curious about?") if topic else ""

if topic:
    with st.expander("Learner Profile", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            learning_goal = st.text_area("What do you want to learn or achieve?", placeholder="Your specific learning objectives")
            interest_focus = st.text_input("Specific areas of interest", placeholder="e.g. Deep Learning, Algorithms")
        with col2:
            knowledge_level = st.selectbox("Your knowledge level:", ["Beginner", "Intermediate", "Advanced"])
            preferred_format = st.selectbox("Preferred format:", ["Text", "Video", "Hands-on"])

        # --- AI Agent Section ---
        st.markdown("###  Ask the AI Agent")
        user_question = st.text_input("Have a specific question about this topic?")

        def get_ai_answer(question, topic):
            try:
                response = co.chat(
                    message=question,
                    chat_history=[],
                    connectors=[],
                    documents=[],
                    preamble=f"You are a helpful tutor assisting a learner with the topic '{topic}'. Keep answers brief and educational."
                )
                return response.text
            except Exception as e:
                return f"Error from AI agent: {str(e)}"

        if user_question:
            with st.spinner("Getting answer from AI Agent..."):
                answer = get_ai_answer(user_question, topic)
                st.markdown(f"**Answer:** {answer}")

    user_profile = {
        "learning_goal": learning_goal or "General understanding",
        "interest_focus": interest_focus or "None specified",
        "knowledge_level": knowledge_level,
        "preferred_format": preferred_format,
        "clarifying_question": clarifying_q or "Not specified"
    }

    if st.button("Generate Learning Report"):
        with st.spinner("Compiling your personalized report..."):
            web_summary, web_source = fetch_from_web(topic)
            video_transcript, video_source = fetch_from_video(topic)
            academic_summary, academic_source = fetch_real_academic_extract(topic)

            research = {
                "web": {"content": web_summary, "source": web_source},
                "video": {"content": video_transcript, "source": video_source},
                "academic": {"content": academic_summary, "source": academic_source}
            }

            report = generate_report(topic, user_profile, research)
            st.session_state.memory[topic] = report

            st.success("Report generated successfully!")
            st.markdown("---")
            st.subheader("Learning Report Preview")

            st.markdown(f"### Web Summary\n\n{web_summary}")
            st.markdown(f"[Read full article]({web_source})")

            st.markdown(f"### Video Summary\n\n{video_transcript}")
            if video_source:
                st.markdown("#### Watch the Video:")
                st.video(video_source)

            st.markdown(f"### Academic Summary\n\n{academic_summary}")
            st.markdown(f"[Read More on Google Scholar]({academic_source})")

            st.markdown("---")
            st.subheader("Full Report")
            st.markdown(report)

            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"{topic.replace(' ', '_')}_learning_report.txt",
                mime="text/plain"
            )

            st.subheader("Concept Flow")
            fig = plot_topic_flow(topic)
            st.pyplot(fig)

            if preferred_format == "Hands-on":
                st.info("🧪 Try building a mini project or solving challenges related to this topic!")
            elif preferred_format == "Text":
                st.info("📚 Consider exploring tutorials, books, or blog posts for deeper reading.")

            refinement = st.text_area("Want to refine or add something to the report?")
            if refinement:
                report += f"\n\n## User Feedback & Additions\n{refinement}"
                st.markdown(report)

    if st.checkbox("Show past reports"):
        for old_topic, old_report in st.session_state.memory.items():
            with st.expander(f"Report: {old_topic}"):
                st.markdown(old_report)
else:
    st.warning("Please enter a topic to begin.")
