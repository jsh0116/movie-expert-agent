---
name: crewai-agent
description: CrewAI 기반 Python 멀티 에이전트 시스템 생성. CrewBase 패턴, YAML 설정, Flow 오케스트레이션, Knowledge Sources, 구조화 출력 포함.
argument-hint: "agent-name description"
---

# CrewAI 에이전트 생성

`$ARGUMENTS`를 기반으로 CrewAI 멀티 에이전트 시스템을 생성한다.
인자가 없으면 사용자에게 에이전트 이름과 목적을 먼저 물어본다.

## 필수 패키지 (pyproject.toml)

```toml
[project]
name = "<agent-name>"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "crewai[tools]>=0.152.0",
    "python-dotenv>=1.1.1",
]
```

웹 스크래핑이 필요하면 `firecrawl-py>=2.16.3` 추가.

## 프로젝트 구조

### Crew 방식 (YAML 설정 기반)

```text
<agent-name>/
├── main.py                # CrewBase 클래스 + kickoff
├── config/
│   ├── agents.yaml        # 에이전트 역할/목표/배경
│   └── tasks.yaml         # 태스크 설명/기대 출력
├── models.py              # Pydantic 출력 모델 (선택)
├── tools.py               # @tool 커스텀 도구
├── .env
└── pyproject.toml
```

### Flow 방식 (상태 기반 파이프라인)

```text
<agent-name>/
├── main.py                # Flow 클래스 + kickoff
├── seo_crew.py            # 평가용 Crew (선택)
├── tools.py               # @tool 커스텀 도구
├── .env
└── pyproject.toml
```

---

## Crew 방식 (YAML 기반)

### agents.yaml

```yaml
researcher_agent:
  role: Senior Research Specialist
  goal: 주어진 주제에 대해 최신 정보를 수집하고 분석
  backstory: 15년 경력의 디지털 리서치 전문가로...
  verbose: true
  inject_date: true
  llm: openai/o4-mini-2025-04-16

writer_agent:
  role: Content Writer
  goal: 리서치 결과를 바탕으로 고품질 콘텐츠 작성
  backstory: ...
  verbose: true
  llm: openai/o4-mini-2025-04-16
```

### tasks.yaml

```yaml
research_task:
  description: >
    {topic}에 대해 최신 정보를 수집하세요.
    최소 5개의 신뢰할 수 있는 출처를 포함해야 합니다.
  expected_output: >
    주제에 대한 구조화된 마크다운 리서치 문서
  agent: researcher_agent
  markdown: true
  output_file: output/research.md
  create_directory: true

writing_task:
  description: >
    리서치 결과를 바탕으로 블로그 포스트를 작성하세요.
  expected_output: >
    2000자 이상의 완성된 블로그 포스트
  agent: writer_agent
  output_file: output/article.md
```

`{topic}` 같은 변수는 `kickoff(inputs={"topic": "..."})` 에서 주입됨.

### CrewBase 클래스

```python
from crewai import Agent, Task, Crew, CrewBase, agent, task, crew
from dotenv import load_dotenv
load_dotenv()

from tools import web_search_tool

@CrewBase
class MyAgentCrew:
    @agent
    def researcher_agent(self):
        return Agent(
            config=self.agents_config["researcher_agent"],
            tools=[web_search_tool],
        )

    @agent
    def writer_agent(self):
        return Agent(config=self.agents_config["writer_agent"])

    @task
    def research_task(self):
        return Task(config=self.tasks_config["research_task"])

    @task
    def writing_task(self):
        return Task(
            config=self.tasks_config["writing_task"],
            context=[self.research_task()],  # 의존성 명시
        )

    @crew
    def crew(self):
        return Crew(agents=self.agents, tasks=self.tasks, verbose=True)

# 실행
result = MyAgentCrew().crew().kickoff(inputs={"topic": "AI Trends"})
for task_output in result.tasks_output:
    print(task_output)
```

### 태스크 의존성 (context)

```python
@task
def final_task(self):
    return Task(
        config=self.tasks_config["final_task"],
        context=[
            self.task_a(),
            self.task_b(),
            self.task_c(),
        ],  # 이전 태스크 출력을 컨텍스트로 받음
    )
```

### 구조화 출력 (output_pydantic)

```python
from pydantic import BaseModel

class Article(BaseModel):
    title: str
    sections: list[str]
    summary: str

@task
def writing_task(self):
    return Task(
        config=self.tasks_config["writing_task"],
        output_pydantic=Article,
    )

# 결과 접근
result = crew.kickoff(inputs={...})
article = result.tasks_output[1].pydantic  # Article 인스턴스
```

---

## Flow 방식 (상태 기반 파이프라인)

복잡한 조건 분기, 반복, 라우팅이 필요한 경우 사용.

```python
from crewai.flow.flow import Flow, start, listen, router, or_
from pydantic import BaseModel

class PipelineState(BaseModel):
    topic: str = ""
    research: str = ""
    content: str = ""
    score: int = 0

class MyPipelineFlow(Flow[PipelineState]):
    @start()
    def initialize(self):
        print(f"주제: {self.state.topic}")

    @listen(initialize)
    def conduct_research(self):
        # 리서치 로직
        self.state.research = "리서치 결과..."

    @router(conduct_research)
    def route_by_type(self):
        if self.state.topic.startswith("blog"):
            return "make_blog"
        return "make_tweet"

    @listen("make_blog")
    def handle_blog(self):
        # 블로그 생성 + 품질 평가
        self.state.score = 8

    @listen("make_tweet")
    def handle_tweet(self):
        self.state.score = 9

    @listen(or_("handle_blog", "handle_tweet"))
    def finalize(self):
        if self.state.score < 7:
            return "remake"  # 재시도 트리거 가능
        print(f"완료! 점수: {self.state.score}")

# 실행
flow = MyPipelineFlow()
flow.kickoff(inputs={"topic": "blog: AI Trends"})
```

### Flow에서 Crew 호출

```python
from crewai import LLM

@listen(conduct_research)
def evaluate_quality(self):
    crew = QualityCrew()
    result = crew.crew().kickoff(inputs={"content": self.state.content})
    self.state.score = result.pydantic.score
```

### LLM 직접 호출

```python
llm = LLM(model="openai/o4-mini", response_format=MyModel)
response = llm.call(messages=[{"role": "user", "content": prompt}])
parsed = MyModel.model_validate_json(response)
```

---

## 도구 정의

```python
from crewai.tools import tool

@tool
def web_search_tool(query: str):
    """웹 검색 도구 - Firecrawl 기반"""
    from firecrawl import FirecrawlApp, ScrapeOptions
    import os

    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = app.search(
        query=query,
        limit=5,
        scrape_options=ScrapeOptions(formats=["markdown"]),
    )
    # 결과 포맷팅
    chunks = []
    for item in response.data:
        chunks.append(f"### {item.metadata.get('title', 'N/A')}\n{item.markdown}")
    return "\n\n".join(chunks)
```

### 빌트인 도구 (crewai_tools)

```python
from crewai_tools import SerperDevTool

search_tool = SerperDevTool(n_results=30)
```

---

## Knowledge Sources (RAG)

```python
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

resume_knowledge = TextFileKnowledgeSource(file_paths=["knowledge/resume.txt"])

@agent
def matching_agent(self):
    return Agent(
        config=self.agents_config["matching_agent"],
        knowledge_sources=[resume_knowledge],
    )
```

`knowledge/` 디렉토리에 텍스트 파일을 두고 에이전트에 주입. 에이전트가 자동으로 RAG 검색.

---

## 실행

```bash
cd <agent-name>
uv sync
uv run python main.py
```

## 참고 문서

- [CrewAI 공식 문서](references/crewai-reference.md)
