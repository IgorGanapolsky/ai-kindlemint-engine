from kindlemint.agents.plot_agent import PlotAgent
from kindlemint.agents.character_agent import CharacterAgent
from kindlemint.agents.dialogue_agent import DialogueAgent
from kindlemint.agents.style_agent import StyleAgent
from kindlemint.agents.market_agent import MarketAgent

class PublishingMoA:
    def __init__(self):
        self.agents = {
            'plot_architect': PlotAgent(),
            'character_developer': CharacterAgent(),
            'dialogue_specialist': DialogueAgent(),
            'style_editor': StyleAgent(),
            'market_optimizer': MarketAgent()
        }

    def create_book(self, concept):
        plot = self.agents['plot_architect'].design(concept)
        characters = self.agents['character_developer'].create(plot)
        dialogue = self.agents['dialogue_specialist'].write(characters, plot)
        styled = self.agents['style_editor'].refine(dialogue)
        optimized = self.agents['market_optimizer'].align(styled)
        return self.aggregate_outputs(plot, characters, dialogue, styled, optimized)

    def aggregate_outputs(self, *components):
        return "\n\n".join(components)
