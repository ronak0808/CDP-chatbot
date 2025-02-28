# **CDP Support Agent Chatbot**  

A chatbot built with Flask and NLP to assist with "how-to" queries related to **Segment, mParticle, Lytics, and Zeotap** by extracting relevant information from official documentation.  

## **Features**  
✅ **Fast and Efficient Search** – Uses **FAISS/Pinecone** for vector-based semantic search.  
✅ **Natural Language Processing** – Processes user queries intelligently with **NLTK and SBERT/OpenAI embeddings**.  
✅ **Multi-CDP Support** – Answers questions about Segment, mParticle, Lytics, and Zeotap.  
✅ **Web-Based UI** – Simple and intuitive interface built with Flask.  
✅ **Real-Time Query Processing** – Retrieves the most relevant documentation excerpts dynamically.  

## **Installation**  

### **1. Clone the Repository**  
git clone https://github.com/ronak0808/CDP-chatbot.git

cd CDP-chatbot


## 2. Create a Virtual Environment
python -m venv venv  

source venv/bin/activate  # macOS/Linux  

venv\Scripts\activate     # Windows  


## 3. Install Dependencies
pip install -r requirements.txt  


## 4. Download Required NLTK Data
python download_nltk_data.py  


## 5. Run the Chatbot
python run.py  


## 6. Access the Chatbot
Open `http://127.0.0.1:5000/` in your browser. 

## **Non-Functional Enhancements**
🔒 Security – Input sanitization and secure API communication.

⚡ Performance Optimization – Efficient indexing with FAISS for quick retrieval.

📈 Scalability – Easily extendable to support additional CDP platforms.

📜 Logging – Tracks errors and user queries in app.log for debugging.
