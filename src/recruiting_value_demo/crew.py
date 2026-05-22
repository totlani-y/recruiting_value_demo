from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool


@CrewBase
class RecruitingValueDemoCrew:
    """Recruiting value demo crew with talent sourcing and screening agents."""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def talent_sourcing_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["talent_sourcing_agent"],  # type: ignore[index]
            tools=[SerperDevTool()],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def screening_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["screening_agent"],  # type: ignore[index]
            verbose=True,
            allow_delegation=False,
        )

    @task
    def source_candidates_task(self) -> Task:
        return Task(
            config=self.tasks_config["source_candidates_task"],  # type: ignore[index]
        )

    @task
    def screen_value_and_shortlist_task(self) -> Task:
        return Task(
            config=self.tasks_config["screen_value_and_shortlist_task"],  # type: ignore[index]
            context=[self.source_candidates_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the recruiting value demo crew."""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
        )