from app.indexer import DocumentIndexer
import logging
import re

logger = logging.getLogger(__name__)

class CDPChatbot:
    def __init__(self):
        self.indexer = DocumentIndexer()
        self.cdps = {
            'segment': ['segment', 'segment.com'],
            'mparticle': ['mparticle', 'mparticle.com'],
            'lytics': ['lytics', 'lytics.com'],
            'zeotap': ['zeotap', 'zeotap.com']
        }
        
    def detect_cdps(self, question):
        """
        Detect which CDP(s) are mentioned in the question.
        Returns a list of CDP names found in the question.
        """
        question = question.lower()
        mentioned_cdps = []
        
        for cdp, keywords in self.cdps.items():
            if any(keyword in question for keyword in keywords):
                mentioned_cdps.append(cdp)
                
        return mentioned_cdps or list(self.cdps.keys())  # If no CDP mentioned, search all

    def is_comparison_question(self, question):
        """
        Determine if the question is asking for a comparison between CDPs.
        """
        question = question.lower()
        comparison_keywords = ['compare', 'comparison', 'versus', 'vs', 'difference', 'better', 'between']
        return any(keyword in question for keyword in comparison_keywords)

    def is_how_to_question(self, question):
        """
        Determine if the question is a how-to question.
        """
        question = question.lower()
        how_to_patterns = [
            r'^how (do|can|to|would|should) (i|you|we)',
            r'^what( is|\'s) the (best way|way) to',
            r'^what are the steps to',
            r'steps (for|to)',
            r'guide (for|to)',
            r'tutorial (for|on)',
            r'process (of|for)',
            r'procedure (for|to)'
        ]
        return any(re.search(pattern, question) for pattern in how_to_patterns)

    def format_comparison_response(self, question, responses):
        """
        Format a response for comparison questions.
        """
        if not responses:
            return "I couldn't find specific comparison information for these CDPs."

        comparison = "Here's how different CDPs handle this:\n\n"
        for cdp, response in responses.items():
            comparison += f"{cdp.capitalize()}:\n{response}\n\n"
        
        return comparison.strip()

    def format_how_to_response(self, response):
        """
        Format a how-to response with clear steps.
        """
        # Try to split on numbered steps or bullet points
        steps = re.split(r'\d+\.|•|-|\*', response)
        steps = [step.strip() for step in steps if step.strip()]
        
        if len(steps) > 1:
            formatted_response = "Here are the steps:\n\n"
            for i, step in enumerate(steps, 1):
                formatted_response += f"{i}. {step}\n"
            return formatted_response
        return response

    def handle_comparison_question(self, question, cdps):
        """
        Handle questions that compare multiple CDPs.
        """
        responses = {}
        for cdp in cdps:
            relevant_docs = self.indexer.search(question, cdp)
            if relevant_docs:
                responses[cdp] = relevant_docs[0]

        return self.format_comparison_response(question, responses)

    def handle_how_to_question(self, question, cdps):
        """
        Handle how-to questions for specific CDPs.
        """
        if len(cdps) == 1:
            relevant_docs = self.indexer.search(question, cdps[0])
            if relevant_docs:
                response = self.format_how_to_response(relevant_docs[0])
                return f"Here's how to do this in {cdps[0].capitalize()}:\n\n{response}"
            return f"I couldn't find specific instructions for this in {cdps[0].capitalize()}'s documentation."
        
        # If multiple CDPs are mentioned but it's not a comparison question
        return self.handle_comparison_question(question, cdps)

    def handle_irrelevant_question(self, question):
        """
        Handle questions that are not related to CDPs.
        """
        return ("I'm a CDP support chatbot. I can help you with questions about Segment, mParticle, "
                "Lytics, and Zeotap. Please ask me how to perform specific tasks in these platforms.")

    def process_question(self, question):
        """
        Main method to process incoming questions and generate responses.
        """
        try:
            # Check if question is CDP-related
            if not any(keyword in question.lower() for cdp in self.cdps for keyword in self.cdps[cdp]):
                return self.handle_irrelevant_question(question)

            # Detect mentioned CDPs
            mentioned_cdps = self.detect_cdps(question)

            # Handle comparison questions
            if self.is_comparison_question(question):
                return self.handle_comparison_question(question, mentioned_cdps)

            # Handle how-to questions
            if self.is_how_to_question(question):
                return self.handle_how_to_question(question, mentioned_cdps)

            # For general questions, treat them as how-to questions
            return self.handle_how_to_question(question, mentioned_cdps)

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return "I encountered an error while processing your question. Please try again."

# Initialize global chatbot instance
chatbot = CDPChatbot()

def process_question(question):
    """
    Global function to process questions using the chatbot instance.
    """
    return chatbot.process_question(question)
