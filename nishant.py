# $ python nishant.py

class Nishant:
    """Forward deployed AI engineer who turns business problems into products people can use."""

    def __init__(self):
        self.role = "Forward Deployed AI Engineer Intern @ ORIX"
        self.study = "MS Computer Science @ Indiana University Bloomington ('27)"
        self.past_life = ["Software Engineer @ Nomura", "SDE Intern @ TCS"]
        self.builds = [
            "enterprise AI products",
            "LLM gateways",
            "evaluation platforms",
            "RAG and analytics agents",
        ]
        self.daily = ["Python", "Java", "C++", "TypeScript"]
        self.based_in = "Bloomington, Indiana"

    def currently(self):
        return [
            "building AI products with business teams at ORIX",
            "shipping Relay, a cost-optimizing LLM gateway",
            "growing Argus, an LLM evaluation and observability platform",
            "open to SWE, AI, and forward deployed engineering opportunities",
        ]

    def fun_fact(self):
        return "My rubber duck got replaced by an LLM. The duck is still bitter."


if __name__ == "__main__":
    me = Nishant()
