import { gql } from 'apollo-server-micro';

export const typeDefs = gql`
  scalar JSON
  scalar DialectSQL

  enum ApiType {
    GENERATE_SQL
    RUN_SQL
    GENERATE_VEGA_CHART
  }

  input ApiHistoryFilterInput {
    apiType: ApiType
    statusCode: Int
    threadId: String
    projectId: Int
    startDate: String
    endDate: String
  }

  input ApiHistoryPaginationInput {
    offset: Int!
    limit: Int!
  }

  type ApiHistoryResponse {
    id: String!
    projectId: Int!
    apiType: ApiType!
    threadId: String
    headers: JSON
    requestPayload: JSON
    responsePayload: JSON
    statusCode: Int
    durationMs: Int
    createdAt: String!
    updatedAt: String!
  }

  type ApiHistoryPaginatedResponse {
    items: [ApiHistoryResponse!]!
    total: Int!
    hasMore: Boolean!
  }

  enum DataSourceName {
    ATHENA
    BIG_QUERY
    DUCKDB
    POSTGRES
    MYSQL
    ORACLE
    MSSQL
    CLICK_HOUSE
    TRINO
    SNOWFLAKE
  }

  enum ExpressionName {
    ABS
    AVG
    COUNT
    COUNT_IF
    MAX
    MIN
    SUM
    CBRT
    CEIL
    CEILING
    EXP
    FLOOR
    LN
    LOG10
    ROUND
    SIGN
    LENGTH
    REVERSE
  }

  enum SampleDatasetName {
    HR
    ECOMMERCE
    NBA
    MUSIC
  }

  enum SyncStatus {
    IN_PROGRESS
    SYNCRONIZED
    UNSYNCRONIZED
  }

  enum SchemaChangeType {
    DELETED_TABLES
    DELETED_COLUMNS
    MODIFIED_COLUMNS
  }

  enum ProjectLanguage {
    EN
    ES
    FR
    ZH_TW
    ZH_CN
    DE
    PT
    RU
    JA
    KO
  }

  type DataSource {
    type: DataSourceName!
    properties: JSON!
    # Show the name if the data source setup comes from a sample
    sampleDataset: SampleDatasetName
  }

  input WhereIdInput {
    id: Int!
  }

  input DataSourceInput {
    type: DataSourceName!
    properties: JSON!
  }

  input SampleDatasetInput {
    name: SampleDatasetName!
  }

  type CompactTable {
    name: String!
    columns: [CompactColumn!]!
    properties: JSON
  }

  input MDLModelSubmitInput {
    name: String!
    columns: [String!]!
  }

  enum RelationType {
    ONE_TO_ONE
    ONE_TO_MANY
    MANY_TO_ONE
  }

  enum OnboardingStatus {
    NOT_STARTED
    DATASOURCE_SAVED
    ONBOARDING_FINISHED
    WITH_SAMPLE_DATASET
  }

  enum NodeType {
    MODEL
    METRIC
    VIEW
    RELATION
    FIELD
    CALCULATED_FIELD
  }

  type Relation {
    fromModelId: Int!
    fromModelReferenceName: String!
    fromColumnId: Int!
    fromColumnReferenceName: String!
    toModelId: Int!
    toModelReferenceName: String!
    toColumnId: Int!
    toColumnReferenceName: String!
    type: RelationType!
    name: String!
  }

  type RecommendRelations {
    id: Int!
    displayName: String!
    referenceName: String!
    relations: [Relation]!
  }

  input RelationInput {
    fromModelId: Int!
    fromColumnId: Int!
    toModelId: Int!
    toColumnId: Int!
    type: RelationType!
  }

  input UpdateRelationInput {
    type: RelationType!
  }

  input SaveRelationInput {
    relations: [RelationInput]!
  }

  input SaveTablesInput {
    tables: [String!]!
  }

  type CompactColumn {
    name: String!
    type: String!
    properties: JSON
  }

  input CustomFieldInput {
    name: String!
    expression: String!
  }

  input CalculatedFieldInput {
    name: String!
    expression: String!
    lineage: [Int!]!
    diagram: JSON
  }

  input CreateModelInput {
    sourceTableName: String!
    fields: [String!]!
    primaryKey: String
  }

  input CreateCalculatedFieldInput {
    modelId: Int!
    name: String!
    expression: ExpressionName!
    lineage: [Int!]!
  }

  input UpdateCalculatedFieldInput {
    name: String!
    expression: ExpressionName!
    lineage: [Int!]!
  }

  input UpdateCalculatedFieldWhere {
    id: Int!
  }

  input ValidateCalculatedFieldInput {
    name: String!
    modelId: Int!
    columnId: Int
  }

  type CalculatedFieldValidationResponse {
    valid: Boolean!
    message: String
  }

  input ModelWhereInput {
    id: Int!
  }

  input UpdateModelInput {
    fields: [String!]!
    primaryKey: String
  }

  # Metadata related
  input UpdateNestedColumnMetadataInput {
    id: Int!
    displayName: String
    description: String
  }

  input UpdateColumnMetadataInput {
    id: Int!
    displayName: String
    description: String
  }

  input UpdateCalculatedFieldMetadataInput {
    id: Int!
    description: String
  }

  input UpdateRelationshipMetadataInput {
    id: Int!
    description: String
  }

  input UpdateViewColumnMetadataInput {
    referenceName: String!
    description: String
  }

  input UpdateModelMetadataInput {
    displayName: String # Model display name, i,e, the alias of the model
    description: String # Model description
    columns: [UpdateColumnMetadataInput!] # Update column metadata
    nestedColumns: [UpdateNestedColumnMetadataInput!] # Update nested column metadata
    calculatedFields: [UpdateCalculatedFieldMetadataInput!] # Update calculated field metadata
    relationships: [UpdateRelationshipMetadataInput!] # Update relationship metadata
  }

  input UpdateViewMetadataInput {
    displayName: String # View display name, i,e, the alias of the view
    description: String # View description
    columns: [UpdateViewColumnMetadataInput!]
  }

  type NestedFieldInfo {
    id: Int!
    displayName: String!
    referenceName: String!
    sourceColumnName: String!
    columnPath: [String!]!
    type: String!
    properties: JSON!
  }

  type FieldInfo {
    id: Int!
    displayName: String!
    referenceName: String!
    sourceColumnName: String!
    type: String
    isCalculated: Boolean!
    notNull: Boolean!
    expression: String
    properties: JSON
    nestedColumns: [NestedFieldInfo!]
  }

  type ModelInfo {
    id: Int!
    displayName: String!
    referenceName: String!
    sourceTableName: String!
    refSql: String
    primaryKey: String
    cached: Boolean!
    refreshTime: String
    description: String
    fields: [FieldInfo]!
    calculatedFields: [FieldInfo]!
    properties: JSON
  }

  type DetailedNestedColumn {
    id: Int!
    displayName: String!
    referenceName: String!
    sourceColumnName: String!
    columnPath: [String!]!
    type: String
    properties: JSON
  }

  type DetailedColumn {
    displayName: String!
    referenceName: String!
    sourceColumnName: String!
    type: String
    isCalculated: Boolean!
    notNull: Boolean!
    properties: JSON!
    nestedColumns: [DetailedNestedColumn!]
  }

  type DetailedRelation {
    fromModelId: Int!
    fromColumnId: Int!
    toModelId: Int!
    toColumnId: Int!
    type: RelationType!
    name: String!
    properties: JSON!
  }

  type DetailedModel {
    displayName: String!
    referenceName: String!
    sourceTableName: String!
    refSql: String!
    primaryKey: String
    cached: Boolean!
    refreshTime: String
    description: String
    fields: [DetailedColumn]
    calculatedFields: [DetailedColumn]
    relations: [DetailedRelation]
    properties: JSON!
  }

  # View
  type ViewInfo {
    id: Int!
    name: String!
    statement: String!
    displayName: String!
  }

  input ViewWhereUniqueInput {
    id: Int!
  }

  input PreviewViewDataInput {
    id: Int!
    # It will return default 500 rows if not specified limit
    # refer: DEFAULT_PREVIEW_LIMIT
    limit: Int
  }

  input CreateViewInput {
    name: String!
    responseId: Int!
  }

  input ValidateViewInput {
    name: String!
  }

  type ViewValidationResponse {
    valid: Boolean!
    message: String
  }

  # onboarding
  type OnboardingStatusResponse {
    status: OnboardingStatus
  }

  type ModelSyncResponse {
    status: SyncStatus!
  }

  type Diagram {
    models: [DiagramModel]!
    views: [DiagramView]!
  }

  type DiagramView {
    id: String!
    viewId: Int!
    nodeType: NodeType!
    statement: String!
    displayName: String!
    referenceName: String!
    fields: [DiagramViewField]!
    description: String
  }

  type DiagramViewField {
    id: String!
    displayName: String!
    referenceName: String!
    type: String!
    nodeType: NodeType!
    description: String
  }

  type DiagramModel {
    id: String!
    modelId: Int!
    nodeType: NodeType!
    displayName: String!
    referenceName: String!
    sourceTableName: String!
    refSql: String
    cached: Boolean!
    refreshTime: String
    description: String
    fields: [DiagramModelField]!
    calculatedFields: [DiagramModelField]!
    relationFields: [DiagramModelRelationField]!
  }

  type DiagramModelNestedField {
    id: String!
    nestedColumnId: Int!
    displayName: String!
    referenceName: String!
    columnPath: [String!]!
    type: String!
    description: String
  }

  type DiagramModelField {
    id: String!
    columnId: Int!
    nodeType: NodeType!
    type: String!
    displayName: String!
    referenceName: String!
    description: String
    isPrimaryKey: Boolean!
    expression: String
    aggregation: String
    lineage: [Int!]
    nestedFields: [DiagramModelNestedField!]
  }

  type DiagramModelRelationField {
    id: String!
    relationId: Int!
    nodeType: NodeType!
    type: RelationType!
    displayName: String!
    referenceName: String!
    description: String
    fromModelId: Int!
    fromModelName: String!
    fromModelDisplayName: String!
    fromColumnId: Int!
    fromColumnName: String!
    fromColumnDisplayName: String!
    toModelId: Int!
    toModelName: String!
    toModelDisplayName: String!
    toColumnId: Int!
    toColumnName: String!
    toColumnDisplayName: String!
  }

  input SimpleMeasureInput {
    name: String!
    type: String!
    isCalculated: Boolean!
    notNull: Boolean!
    properties: JSON!
  }

  input DimensionInput {
    name: String!
    type: String!
    isCalculated: Boolean!
    notNull: Boolean!
    properties: JSON!
  }

  input TimeGrainInput {
    name: String!
    refColumn: String!
    dateParts: [String!]!
  }

  input CreateSimpleMetricInput {
    name: String!
    displayName: String!
    description: String
    cached: Boolean!
    refreshTime: String
    model: String!
    properties: JSON!
    measure: [SimpleMeasureInput!]!
    dimension: [DimensionInput!]!
    timeGrain: [TimeGrainInput!]!
  }

  # Task
  type Task {
    id: String!
  }

  # Error
  type Error {
    code: String
    shortMessage: String
    message: String
    stacktrace: [String]
  }

  # Asking Task
  input AskingTaskInput {
    question: String!
    # Used for follow-up questions
    threadId: Int
  }

  enum AskingTaskStatus {
    UNDERSTANDING
    SEARCHING
    PLANNING
    GENERATING
    CORRECTING
    FINISHED
    FAILED
    STOPPED
  }

  enum AskingTaskType {
    GENERAL
    TEXT_TO_SQL
    MISLEADING_QUERY
  }

  enum ChartTaskStatus {
    FETCHING
    GENERATING
    FINISHED
    FAILED
    STOPPED
  }

  enum ChartType {
    BAR
    PIE
    LINE
    MULTI_LINE
    AREA
    GROUPED_BAR
    STACKED_BAR
  }

  enum ResultCandidateType {
    VIEW # View type candidate is provided basd on a saved view
    LLM # LLM type candidate is created by LLM
    SQL_PAIR # SQL pair type candidate is created by SQL pair
  }

  type ResultCandidate {
    type: ResultCandidateType!
    sql: String!
    view: ViewInfo
    sqlPair: SqlPair
  }

  type AskingTask {
    status: AskingTaskStatus!
    type: AskingTaskType
    error: Error
    candidates: [ResultCandidate!]!
    rephrasedQuestion: String
    intentReasoning: String
    sqlGenerationReasoning: String
    retrievedTables: [String!]
    invalidSql: String
    traceId: String
    queryId: String
  }

  input InstantRecommendedQuestionsInput {
    previousQuestions: [String!]
  }

  enum RecommendedQuestionsTaskStatus {
    NOT_STARTED
    GENERATING
    FINISHED
    FAILED
  }

  type ResultQuestion {
    question: String!
    category: String!
    sql: String!
  }

  type RecommendedQuestionsTask {
    status: RecommendedQuestionsTaskStatus!
    questions: [ResultQuestion!]!
    error: Error
  }

  # Thread
  input CreateThreadInput {
    question: String
    sql: String
    taskId: String
  }

  input CreateThreadResponseInput {
    question: String
    sql: String
    taskId: String
  }

  input ThreadUniqueWhereInput {
    id: Int!
  }

  input UpdateThreadInput {
    summary: String
  }

  input ThreadResponseUniqueWhereInput {
    id: Int!
  }

  input UpdateThreadResponseInput {
    sql: String
  }

  input AdjustThreadResponseChartInput {
    chartType: ChartType!
    xAxis: String
    yAxis: String
    xOffset: String
    color: String
    theta: String
  }

  input AdjustThreadResponseInput {
    tables: [String!]
    sqlGenerationReasoning: String
    sql: String
  }

  input PreviewDataInput {
    responseId: Int!
    # Optional, only used for preview data of a single step
    stepIndex: Int
    # It will return default 500 rows if not specified limit
    # refer: DEFAULT_PREVIEW_LIMIT
    limit: Int
  }

  type DetailStep {
    summary: String!
    sql: String!
    cteName: String
  }

  enum ThreadResponseAnswerStatus {
    NOT_STARTED
    FETCHING_DATA
    PREPROCESSING
    STREAMING
    FINISHED
    FAILED
    INTERRUPTED
  }

  type ThreadResponseAnswerDetail {
    queryId: String
    status: ThreadResponseAnswerStatus
    error: Error
    numRowsUsedInLLM: Int
    content: String
  }

  type ThreadResponseBreakdownDetail {
    queryId: String
    status: AskingTaskStatus!
    error: Error
    description: String
    steps: [DetailStep!]
  }

  type ThreadResponseChartDetail {
    queryId: String
    status: ChartTaskStatus!
    error: Error
    description: String
    chartType: ChartType
    chartSchema: JSON
    adjustment: Boolean
  }

  enum ThreadResponseAdjustmentType {
    REASONING
    APPLY_SQL
  }

  type ThreadResponseAdjustment {
    type: ThreadResponseAdjustmentType!
    payload: JSON
  }

  type AdjustmentTask {
    queryId: String
    status: AskingTaskStatus
    error: Error
    sql: String
    traceId: String
    invalidSql: String
  }

  type ThreadResponse {
    id: Int!
    threadId: Int!
    question: String!
    sql: String
    view: ViewInfo
    breakdownDetail: ThreadResponseBreakdownDetail
    answerDetail: ThreadResponseAnswerDetail
    chartDetail: ThreadResponseChartDetail
    askingTask: AskingTask
    adjustment: ThreadResponseAdjustment
    adjustmentTask: AdjustmentTask
  }

  # Thread only consists of basic information of a thread
  type Thread {
    id: Int!
    summary: String!
  }

  # Detailed thread consists of thread and thread responses
  type DetailedThread {
    id: Int!
    responses: [ThreadResponse!]!
  }

  type SuggestedQuestion {
    question: String!
    label: String!
  }
  # Ask Questions Responses
  type SuggestedQuestionResponse {
    questions: [SuggestedQuestion]!
  }

  # Settings
  input UpdateDataSourceInput {
    properties: JSON!
  }

  input UpdateCurrentProjectInput {
    language: ProjectLanguage!
  }

  type Settings {
    productVersion: String!
    dataSource: DataSource!
    language: ProjectLanguage!
  }

  type GetMDLResult {
    hash: String!
    mdl: String
  }

  input PreviewSQLDataInput {
    sql: String!
    projectId: String
    limit: Int
    dryRun: Boolean
  }

  # Schema Change
  type SchemaChange {
    deletedTables: [DetailedChangeTable!]
    deletedColumns: [DetailedChangeTable!]
    modifiedColumns: [DetailedChangeTable!]
    lastSchemaChangeTime: String
  }

  type DetailedChangeTable {
    sourceTableName: String!
    displayName: String!
    columns: [DetailedChangeColumn!]!
    calculatedFields: [DetailedAffectedCalculatedFields!]!
    relationships: [DetailedAffectedRelationships!]!
  }

  type DetailedChangeColumn {
    sourceColumnName: String!
    displayName: String!
    type: String!
  }

  type DetailedAffectedCalculatedFields {
    displayName: String!
    referenceName: String!
    type: String!
  }

  type DetailedAffectedRelationships {
    displayName: String!
    referenceName: String!
  }

  input ResolveSchemaChangeWhereInput {
    type: SchemaChangeType!
  }

  # Learning
  type LearningRecord {
    paths: [String!]!
  }

  input SaveLearningRecordInput {
    path: String!
  }

  # Dashboard
  enum DashboardItemType {
    BAR
    PIE
    LINE
    MULTI_LINE
    AREA
    GROUPED_BAR
    STACKED_BAR
    TABLE
    NUMBER
  }

  input DashboardItemWhereInput {
    id: Int!
  }

  input CreateDashboardItemInput {
    itemType: DashboardItemType!
    responseId: Int!
  }

  input UpdateDashboardItemInput {
    displayName: String!
  }

  input ItemLayoutInput {
    itemId: Int!
    x: Int!
    y: Int!
    w: Int!
    h: Int!
  }

  input UpdateDashboardItemLayoutsInput {
    layouts: [ItemLayoutInput!]!
  }

  input DeleteDashboardItemInput {
    itemId: Int!
  }

  input PreviewItemSQLInput {
    itemId: Int!
    limit: Int
    refresh: Boolean = false
  }

  type PreviewItemResponse {
    data: JSON!
    cacheHit: Boolean!
    cacheCreatedAt: String
    cacheOverrodeAt: String
    override: Boolean!
  }

  input SetDashboardScheduleInput {
    cacheEnabled: Boolean!
    schedule: SetDashboardScheduleData
  }

  type DashboardSchedule {
    frequency: ScheduleFrequencyEnum
    hour: Int
    minute: Int
    day: CacheScheduleDayEnum
    timezone: String
    cron: String
  }

  input SetDashboardScheduleData {
    frequency: ScheduleFrequencyEnum!
    hour: Int
    minute: Int
    day: CacheScheduleDayEnum
    timezone: String
    cron: String
  }

  enum ScheduleFrequencyEnum {
    DAILY
    WEEKLY
    CUSTOM
    NEVER
  }

  enum CacheScheduleDayEnum {
    SUN
    MON
    TUE
    WED
    THU
    FRI
    SAT
  }

  type DashboardItemLayout {
    x: Int!
    y: Int!
    w: Int!
    h: Int!
  }

  type DashboardItemDetail {
    sql: String!
    chartSchema: JSON
  }

  type DashboardItem {
    id: Int!
    dashboardId: Int!
    type: DashboardItemType!
    layout: DashboardItemLayout!
    detail: DashboardItemDetail!
    displayName: String
  }

  type Dashboard {
    id: Int!
    projectId: Int!
    name: String!
    cacheEnabled: Boolean!
    scheduleFrequency: ScheduleFrequencyEnum
    scheduleTimezone: String
    scheduleCron: String
    nextScheduledAt: String
  }

  type DetailedDashboard {
    id: Int!
    name: String!
    description: String
    cacheEnabled: Boolean!
    nextScheduledAt: String
    schedule: DashboardSchedule
    items: [DashboardItem!]!
  }

  type SqlPair {
    id: Int!
    projectId: Int!
    sql: String!
    question: String!
    createdAt: String
    updatedAt: String
  }

  input CreateSqlPairInput {
    sql: String!
    question: String!
  }

  input UpdateSqlPairInput {
    sql: String
    question: String
  }

  input SqlPairWhereUniqueInput {
    id: Int!
  }

  input GenerateQuestionInput {
    sql: String!
  }

  input ModelSubstituteInput {
    sql: DialectSQL!
  }

  type Instruction {
    id: Int!
    projectId: Int!
    instruction: String!
    questions: [String!]!
    isDefault: Boolean!
    createdAt: String!
    updatedAt: String!
  }

  input CreateInstructionInput {
    instruction: String!
    questions: [String!]!
    isDefault: Boolean!
  }

  input UpdateInstructionInput {
    instruction: String
    questions: [String!]
    isDefault: Boolean
  }

  input InstructionWhereInput {
    id: Int!
  }

  # Query and Mutation
  type Query {
    # On Boarding Steps
    listDataSourceTables: [CompactTable!]!
    autoGenerateRelation: [RecommendRelations!]!
    onboardingStatus: OnboardingStatusResponse!

    # Modeling Page
    listModels: [ModelInfo!]!
    model(where: ModelWhereInput!): DetailedModel!
    modelSync: ModelSyncResponse!
    diagram: Diagram!
    schemaChange: SchemaChange!

    # View
    listViews: [ViewInfo!]!
    view(where: ViewWhereUniqueInput!): ViewInfo!

    # Ask
    askingTask(taskId: String!): AskingTask
    suggestedQuestions: SuggestedQuestionResponse!
    threads: [Thread!]!
    thread(threadId: Int!): DetailedThread!
    threadResponse(responseId: Int!): ThreadResponse!
    nativeSql(responseId: Int!): String!

    # Adjustment
    adjustmentTask(taskId: String!): AdjustmentTask

    # Settings
    settings: Settings!

    # System
    getMDL(hash: String!): GetMDLResult!

    # Learning
    learningRecord: LearningRecord!

    # Recommendation questions
    getThreadRecommendationQuestions(threadId: Int!): RecommendedQuestionsTask!
    getProjectRecommendationQuestions: RecommendedQuestionsTask!
    instantRecommendedQuestions(taskId: String!): RecommendedQuestionsTask!

    # Dashboard
    dashboardItems: [DashboardItem!]!
    dashboard: DetailedDashboard!

    # SQL Pairs
    sqlPairs: [SqlPair]!
    # Instructions
    instructions: [Instruction]!

    # Api History
    apiHistory(
      filter: ApiHistoryFilterInput
      pagination: ApiHistoryPaginationInput!
    ): ApiHistoryPaginatedResponse!
  }

  type Mutation {
    # On Boarding Steps
    saveDataSource(data: DataSourceInput!): DataSource!
    startSampleDataset(data: SampleDatasetInput!): JSON!
    saveTables(data: SaveTablesInput!): JSON!
    saveRelations(data: SaveRelationInput!): JSON!
    deploy(force: Boolean): JSON!

    # Modeling Page
    createModel(data: CreateModelInput!): JSON!
    updateModel(where: ModelWhereInput!, data: UpdateModelInput!): JSON!
    deleteModel(where: ModelWhereInput!): Boolean!
    previewModelData(where: WhereIdInput!): JSON!
    triggerDataSourceDetection: Boolean!
    resolveSchemaChange(where: ResolveSchemaChangeWhereInput!): Boolean!

    # Metadata
    updateModelMetadata(
      where: ModelWhereInput!
      data: UpdateModelMetadataInput!
    ): Boolean!
    updateViewMetadata(
      where: ViewWhereUniqueInput!
      data: UpdateViewMetadataInput!
    ): Boolean!

    # Relation
    createRelation(data: RelationInput!): JSON!
    updateRelation(data: UpdateRelationInput!, where: WhereIdInput!): JSON!
    deleteRelation(where: WhereIdInput!): Boolean!

    # Calculated field
    createCalculatedField(data: CreateCalculatedFieldInput!): JSON!
    updateCalculatedField(
      where: UpdateCalculatedFieldWhere!
      data: UpdateCalculatedFieldInput!
    ): JSON!
    deleteCalculatedField(where: UpdateCalculatedFieldWhere): Boolean!
    validateCalculatedField(
      data: ValidateCalculatedFieldInput!
    ): CalculatedFieldValidationResponse!

    # View
    createView(data: CreateViewInput!): ViewInfo!
    deleteView(where: ViewWhereUniqueInput!): Boolean!
    previewViewData(where: PreviewViewDataInput!): JSON!
    validateView(data: ValidateViewInput!): ViewValidationResponse!

    # Ask
    createAskingTask(data: AskingTaskInput!): Task!
    cancelAskingTask(taskId: String!): Boolean!
    rerunAskingTask(responseId: Int!): Task!

    # Thread
    createThread(data: CreateThreadInput!): Thread!
    updateThread(
      where: ThreadUniqueWhereInput!
      data: UpdateThreadInput!
    ): Thread!
    deleteThread(where: ThreadUniqueWhereInput!): Boolean!

    # Thread Response
    createThreadResponse(
      threadId: Int!
      data: CreateThreadResponseInput!
    ): ThreadResponse!
    updateThreadResponse(
      where: ThreadResponseUniqueWhereInput!
      data: UpdateThreadResponseInput!
    ): ThreadResponse!
    previewData(where: PreviewDataInput!): JSON!
    previewBreakdownData(where: PreviewDataInput!): JSON!

    # Generate Thread Response Breakdown
    generateThreadResponseBreakdown(responseId: Int!): ThreadResponse!

    # Generate Thread Response Answer
    generateThreadResponseAnswer(responseId: Int!): ThreadResponse!

    # Generate Thread Response Chart
    generateThreadResponseChart(responseId: Int!): ThreadResponse!

    # Adjust Thread Response Chart
    adjustThreadResponseChart(
      responseId: Int!
      data: AdjustThreadResponseChartInput!
    ): ThreadResponse!

    # Adjustment
    adjustThreadResponse(
      responseId: Int!
      data: AdjustThreadResponseInput!
    ): ThreadResponse!
    cancelAdjustmentTask(taskId: String!): Boolean!
    rerunAdjustmentTask(responseId: Int!): Boolean!

    # Settings
    resetCurrentProject: Boolean!
    updateCurrentProject(data: UpdateCurrentProjectInput!): Boolean!
    updateDataSource(data: UpdateDataSourceInput!): DataSource!

    # preview
    previewSql(data: PreviewSQLDataInput): JSON!

    # Learning
    saveLearningRecord(data: SaveLearningRecordInput!): LearningRecord!

    # Recommendation questions
    generateThreadRecommendationQuestions(threadId: Int!): Boolean!
    generateProjectRecommendationQuestions: Boolean!
    createInstantRecommendedQuestions(
      data: InstantRecommendedQuestionsInput!
    ): Task!

    # Dashboard
    updateDashboardItemLayouts(
      data: UpdateDashboardItemLayoutsInput!
    ): [DashboardItem!]!
    createDashboardItem(data: CreateDashboardItemInput!): DashboardItem!
    updateDashboardItem(
      where: DashboardItemWhereInput!
      data: UpdateDashboardItemInput!
    ): DashboardItem!
    deleteDashboardItem(where: DashboardItemWhereInput!): Boolean!
    previewItemSQL(data: PreviewItemSQLInput!): PreviewItemResponse!
    setDashboardSchedule(data: SetDashboardScheduleInput!): Dashboard!

    # SQL Pairs
    createSqlPair(data: CreateSqlPairInput!): SqlPair!
    updateSqlPair(
      where: SqlPairWhereUniqueInput!
      data: UpdateSqlPairInput!
    ): SqlPair!
    deleteSqlPair(where: SqlPairWhereUniqueInput!): Boolean!
    generateQuestion(data: GenerateQuestionInput!): String!
    modelSubstitute(data: ModelSubstituteInput!): String!
    # Instructions
    createInstruction(data: CreateInstructionInput!): Instruction!
    updateInstruction(
      where: InstructionWhereInput!
      data: UpdateInstructionInput!
    ): Instruction!
    deleteInstruction(where: InstructionWhereInput!): Boolean!
  }
`;
