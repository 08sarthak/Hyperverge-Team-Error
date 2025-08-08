## RAG-Enhanced Lesson Plan Generation Graph

**File Location:** `app/utils_rag/graph_rag.py`  
**State Type:** `RagLessonPlanStateWithReview`

Enhanced workflow using RAG (Retrieval Augmented Generation) for lesson plan creation

### 🎯 Key Features

- RAG-enhanced content generation
- Topic-specific retrieval
- Enhanced web resource fetching
- Quality review and revision
- Structured output with RAG agents

### 📊 Graph Structure

```mermaid
graph TD
    prompt["prompt[generate_user_prompt]Generates user prompt with lesson plan p..."]
    points["points[points_lesson_plan_generator]Generates lesson plan outline using RAG ..."]
    detailed_lesson_plan["detailed_lesson_plan[detailed_lesson_plan_generator]Generates detailed RAG-enhanced lesson p..."]
    review_lesson_plan["review_lesson_plan[review_lesson_plan_node]Reviews RAG-generated lesson plan for qu..."]
    START(["🚀 START"])
    END(["🏁 END"])
    START --> prompt
    prompt --> points
    points --> detailed_lesson_plan
    detailed_lesson_plan --> review_lesson_plan
    review_lesson_plan -->|"revise"| detailed_lesson_plan
    review_lesson_plan -->|"approve"| END
    classDef startEnd fill:#667eea,stroke:#764ba2,stroke-width:3px,color:#fff
    classDef processNode fill:#f8fafc,stroke:#667eea,stroke-width:2px
    class START,END startEnd
    class prompt,points,detailed_lesson_plan,review_lesson_plan processNode
```

### 🔧 Node Details


#### prompt
- **Function:** `generate_user_prompt`
- **Description:** Generates user prompt with lesson plan parameters including topic
- **Inputs:** `grade`, `subject`, `chapter_number`, `chapter_name`, `number_of_lecture`, `duration_of_lecture`, `class_strength`, `content`, `topic`
- **Outputs:** `user_prompt`

#### points
- **Function:** `points_lesson_plan_generator`
- **Description:** Generates lesson plan outline using RAG techniques
- **Inputs:** `user_prompt`
- **Outputs:** `lesson_plan_points`

#### detailed_lesson_plan
- **Function:** `detailed_lesson_plan_generator`
- **Description:** Generates detailed RAG-enhanced lesson plan content
- **Inputs:** `lesson_plan_points`, `number_of_lecture`, `structured_output`
- **Outputs:** `lesson_plan`, `revision_count`

#### review_lesson_plan
- **Function:** `review_lesson_plan_node`
- **Description:** Reviews RAG-generated lesson plan for quality
- **Inputs:** `lesson_plan`, `grade`, `subject`, `language`
- **Outputs:** `review_results`, `needs_revision`, `review_completed`


### 🔄 Flow Control

**Regular Edges:**
- `START` → `prompt`
- `prompt` → `points`
- `points` → `detailed_lesson_plan`
- `detailed_lesson_plan` → `review_lesson_plan`

**Conditional Edges:**
- **review_lesson_plan** (`should_revise_decision`):
  - `revise` → `detailed_lesson_plan`
  - `approve` → `END`
