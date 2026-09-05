> [← Project README](../../README.md)

# Table of Contents

* [omega\_vision.adapters.adapters](#omega_vision.adapters.adapters)
  * [LearnedPartRoleProvider](#omega_vision.adapters.adapters.LearnedPartRoleProvider)
    * [\_\_init\_\_](#omega_vision.adapters.adapters.LearnedPartRoleProvider.__init__)
    * [infer\_part\_roles](#omega_vision.adapters.adapters.LearnedPartRoleProvider.infer_part_roles)
  * [normalize\_grid\_structure](#omega_vision.adapters.adapters.normalize_grid_structure)
  * [normalize\_image\_structure](#omega_vision.adapters.adapters.normalize_image_structure)
  * [GridPerceptionBatch](#omega_vision.adapters.adapters.GridPerceptionBatch)
    * [observation](#omega_vision.adapters.adapters.GridPerceptionBatch.observation)
    * [candidates](#omega_vision.adapters.adapters.GridPerceptionBatch.candidates)
    * [extractor\_details](#omega_vision.adapters.adapters.GridPerceptionBatch.extractor_details)
  * [MediaPerceptionBatch](#omega_vision.adapters.adapters.MediaPerceptionBatch)
    * [observation](#omega_vision.adapters.adapters.MediaPerceptionBatch.observation)
    * [candidates](#omega_vision.adapters.adapters.MediaPerceptionBatch.candidates)
    * [extractor\_details](#omega_vision.adapters.adapters.MediaPerceptionBatch.extractor_details)
  * [PerceptionAdapter](#omega_vision.adapters.adapters.PerceptionAdapter)
    * [propose\_candidates](#omega_vision.adapters.adapters.PerceptionAdapter.propose_candidates)
  * [GridAdapter](#omega_vision.adapters.adapters.GridAdapter)
    * [\_\_init\_\_](#omega_vision.adapters.adapters.GridAdapter.__init__)
    * [normalize](#omega_vision.adapters.adapters.GridAdapter.normalize)
    * [candidate\_detail](#omega_vision.adapters.adapters.GridAdapter.candidate_detail)
    * [propose\_candidates](#omega_vision.adapters.adapters.GridAdapter.propose_candidates)
  * [ImageAdapter](#omega_vision.adapters.adapters.ImageAdapter)
    * [\_\_init\_\_](#omega_vision.adapters.adapters.ImageAdapter.__init__)
    * [normalize](#omega_vision.adapters.adapters.ImageAdapter.normalize)
    * [candidate\_detail](#omega_vision.adapters.adapters.ImageAdapter.candidate_detail)
    * [propose\_candidates](#omega_vision.adapters.adapters.ImageAdapter.propose_candidates)
  * [SimpleVideoAdapter](#omega_vision.adapters.adapters.SimpleVideoAdapter)
    * [\_\_init\_\_](#omega_vision.adapters.adapters.SimpleVideoAdapter.__init__)
    * [normalize](#omega_vision.adapters.adapters.SimpleVideoAdapter.normalize)
    * [propose\_candidates](#omega_vision.adapters.adapters.SimpleVideoAdapter.propose_candidates)
* [omega\_vision.adapters.providers](#omega_vision.adapters.providers)
  * [ProviderCapabilities](#omega_vision.adapters.providers.ProviderCapabilities)
    * [mode](#omega_vision.adapters.providers.ProviderCapabilities.mode)
    * [candidate\_parts](#omega_vision.adapters.providers.ProviderCapabilities.candidate_parts)
    * [semantic\_record\_families](#omega_vision.adapters.providers.ProviderCapabilities.semantic_record_families)
    * [dynamic\_candidate\_parts](#omega_vision.adapters.providers.ProviderCapabilities.dynamic_candidate_parts)
    * [supports\_candidate\_part](#omega_vision.adapters.providers.ProviderCapabilities.supports_candidate_part)
  * [UnsupportedProviderCapability](#omega_vision.adapters.providers.UnsupportedProviderCapability)
    * [\_\_init\_\_](#omega_vision.adapters.providers.UnsupportedProviderCapability.__init__)
    * [as\_dict](#omega_vision.adapters.providers.UnsupportedProviderCapability.as_dict)
  * [ArtifactProvider](#omega_vision.adapters.providers.ArtifactProvider)
    * [mode](#omega_vision.adapters.providers.ArtifactProvider.mode)
    * [capabilities](#omega_vision.adapters.providers.ArtifactProvider.capabilities)
    * [get\_candidate\_part](#omega_vision.adapters.providers.ArtifactProvider.get_candidate_part)
  * [PythonProvider](#omega_vision.adapters.providers.PythonProvider)
    * [mode](#omega_vision.adapters.providers.PythonProvider.mode)
    * [\_\_init\_\_](#omega_vision.adapters.providers.PythonProvider.__init__)
    * [capabilities](#omega_vision.adapters.providers.PythonProvider.capabilities)
    * [get\_candidate\_part](#omega_vision.adapters.providers.PythonProvider.get_candidate_part)
  * [GptArtifactProvider](#omega_vision.adapters.providers.GptArtifactProvider)
    * [mode](#omega_vision.adapters.providers.GptArtifactProvider.mode)
    * [ARTIFACT\_NAMES](#omega_vision.adapters.providers.GptArtifactProvider.ARTIFACT_NAMES)
    * [\_\_init\_\_](#omega_vision.adapters.providers.GptArtifactProvider.__init__)
    * [capabilities](#omega_vision.adapters.providers.GptArtifactProvider.capabilities)
    * [get\_candidate\_part](#omega_vision.adapters.providers.GptArtifactProvider.get_candidate_part)
  * [PrologProvider](#omega_vision.adapters.providers.PrologProvider)
    * [mode](#omega_vision.adapters.providers.PrologProvider.mode)
    * [SEMANTIC\_NAMESPACES](#omega_vision.adapters.providers.PrologProvider.SEMANTIC_NAMESPACES)
    * [\_\_init\_\_](#omega_vision.adapters.providers.PrologProvider.__init__)
    * [capabilities](#omega_vision.adapters.providers.PrologProvider.capabilities)
    * [get\_candidate\_part](#omega_vision.adapters.providers.PrologProvider.get_candidate_part)
    * [get\_semantic\_records](#omega_vision.adapters.providers.PrologProvider.get_semantic_records)
* [omega\_vision.adapters.sprite](#omega_vision.adapters.sprite)
  * [AlphaContourProvider](#omega_vision.adapters.sprite.AlphaContourProvider)
    * [\_\_call\_\_](#omega_vision.adapters.sprite.AlphaContourProvider.__call__)
  * [SpriteAdapter](#omega_vision.adapters.sprite.SpriteAdapter)
    * [\_\_init\_\_](#omega_vision.adapters.sprite.SpriteAdapter.__init__)
* [omega\_vision.core.learning](#omega_vision.core.learning)
  * [TransitionRecord](#omega_vision.core.learning.TransitionRecord)
    * [before\_state\_id](#omega_vision.core.learning.TransitionRecord.before_state_id)
    * [action\_or\_event](#omega_vision.core.learning.TransitionRecord.action_or_event)
    * [after\_state\_id](#omega_vision.core.learning.TransitionRecord.after_state_id)
    * [changes](#omega_vision.core.learning.TransitionRecord.changes)
    * [provenance](#omega_vision.core.learning.TransitionRecord.provenance)
  * [TransformationCandidate](#omega_vision.core.learning.TransformationCandidate)
    * [candidate\_id](#omega_vision.core.learning.TransformationCandidate.candidate_id)
    * [transformation](#omega_vision.core.learning.TransformationCandidate.transformation)
    * [evidence](#omega_vision.core.learning.TransformationCandidate.evidence)
    * [score](#omega_vision.core.learning.TransformationCandidate.score)
    * [source\_state\_id](#omega_vision.core.learning.TransformationCandidate.source_state_id)
    * [target\_state\_id](#omega_vision.core.learning.TransformationCandidate.target_state_id)
    * [action\_or\_event](#omega_vision.core.learning.TransformationCandidate.action_or_event)
    * [assumptions](#omega_vision.core.learning.TransformationCandidate.assumptions)
    * [critiques](#omega_vision.core.learning.TransformationCandidate.critiques)
    * [provenance](#omega_vision.core.learning.TransformationCandidate.provenance)
  * [RuleEvidence](#omega_vision.core.learning.RuleEvidence)
    * [rule\_id](#omega_vision.core.learning.RuleEvidence.rule_id)
    * [confirming](#omega_vision.core.learning.RuleEvidence.confirming)
    * [refuting](#omega_vision.core.learning.RuleEvidence.refuting)
  * [RuleRivalSet](#omega_vision.core.learning.RuleRivalSet)
    * [rules](#omega_vision.core.learning.RuleRivalSet.rules)
  * [PredictionGradeStatus](#omega_vision.core.learning.PredictionGradeStatus)
    * [SUCCESS](#omega_vision.core.learning.PredictionGradeStatus.SUCCESS)
    * [FAILURE](#omega_vision.core.learning.PredictionGradeStatus.FAILURE)
    * [PARTIAL\_MATCH](#omega_vision.core.learning.PredictionGradeStatus.PARTIAL_MATCH)
    * [CONTRADICTION](#omega_vision.core.learning.PredictionGradeStatus.CONTRADICTION)
    * [UNGRADABLE](#omega_vision.core.learning.PredictionGradeStatus.UNGRADABLE)
  * [PredictionGrade](#omega_vision.core.learning.PredictionGrade)
    * [score](#omega_vision.core.learning.PredictionGrade.score)
    * [evidence](#omega_vision.core.learning.PredictionGrade.evidence)
    * [status](#omega_vision.core.learning.PredictionGrade.status)
    * [\_\_post\_init\_\_](#omega_vision.core.learning.PredictionGrade.__post_init__)
  * [TransitionAnalyzer](#omega_vision.core.learning.TransitionAnalyzer)
    * [\_\_init\_\_](#omega_vision.core.learning.TransitionAnalyzer.__init__)
    * [analyze](#omega_vision.core.learning.TransitionAnalyzer.analyze)
  * [TransformationLearner](#omega_vision.core.learning.TransformationLearner)
    * [\_\_init\_\_](#omega_vision.core.learning.TransformationLearner.__init__)
    * [learn](#omega_vision.core.learning.TransformationLearner.learn)
  * [RuleInducer](#omega_vision.core.learning.RuleInducer)
    * [\_\_init\_\_](#omega_vision.core.learning.RuleInducer.__init__)
    * [induce](#omega_vision.core.learning.RuleInducer.induce)
  * [RuleRanker](#omega_vision.core.learning.RuleRanker)
    * [\_\_init\_\_](#omega_vision.core.learning.RuleRanker.__init__)
    * [rank](#omega_vision.core.learning.RuleRanker.rank)
  * [RuleExecutor](#omega_vision.core.learning.RuleExecutor)
    * [\_\_init\_\_](#omega_vision.core.learning.RuleExecutor.__init__)
    * [applicable](#omega_vision.core.learning.RuleExecutor.applicable)
    * [apply](#omega_vision.core.learning.RuleExecutor.apply)
  * [OutcomeChannel](#omega_vision.core.learning.OutcomeChannel)
    * [\_\_init\_\_](#omega_vision.core.learning.OutcomeChannel.__init__)
    * [read](#omega_vision.core.learning.OutcomeChannel.read)
  * [PredictionEvaluator](#omega_vision.core.learning.PredictionEvaluator)
    * [\_\_init\_\_](#omega_vision.core.learning.PredictionEvaluator.__init__)
    * [evaluate](#omega_vision.core.learning.PredictionEvaluator.evaluate)
  * [LearningStepResult](#omega_vision.core.learning.LearningStepResult)
    * [transition](#omega_vision.core.learning.LearningStepResult.transition)
    * [candidates](#omega_vision.core.learning.LearningStepResult.candidates)
    * [rules](#omega_vision.core.learning.LearningStepResult.rules)
  * [GameLearningPipeline](#omega_vision.core.learning.GameLearningPipeline)
    * [\_\_init\_\_](#omega_vision.core.learning.GameLearningPipeline.__init__)
    * [learn\_transition](#omega_vision.core.learning.GameLearningPipeline.learn_transition)
    * [recommend\_action](#omega_vision.core.learning.GameLearningPipeline.recommend_action)
    * [predict](#omega_vision.core.learning.GameLearningPipeline.predict)
    * [grade\_prediction](#omega_vision.core.learning.GameLearningPipeline.grade_prediction)
* [omega\_vision.core.memory](#omega_vision.core.memory)
  * [EncounterLog](#omega_vision.core.memory.EncounterLog)
    * [\_\_init\_\_](#omega_vision.core.memory.EncounterLog.__init__)
    * [append](#omega_vision.core.memory.EncounterLog.append)
    * [get](#omega_vision.core.memory.EncounterLog.get)
    * [records](#omega_vision.core.memory.EncounterLog.records)
    * [for\_object](#omega_vision.core.memory.EncounterLog.for_object)
    * [replay](#omega_vision.core.memory.EncounterLog.replay)
    * [deterministic\_hash](#omega_vision.core.memory.EncounterLog.deterministic_hash)
  * [ResidualGate](#omega_vision.core.memory.ResidualGate)
    * [evaluate](#omega_vision.core.memory.ResidualGate.evaluate)
  * [SymbolicMemory](#omega_vision.core.memory.SymbolicMemory)
    * [\_\_init\_\_](#omega_vision.core.memory.SymbolicMemory.__init__)
    * [get](#omega_vision.core.memory.SymbolicMemory.get)
    * [all\_atoms](#omega_vision.core.memory.SymbolicMemory.all_atoms)
    * [events](#omega_vision.core.memory.SymbolicMemory.events)
    * [evidence\_for](#omega_vision.core.memory.SymbolicMemory.evidence_for)
    * [identity\_decision](#omega_vision.core.memory.SymbolicMemory.identity_decision)
    * [confidence\_history](#omega_vision.core.memory.SymbolicMemory.confidence_history)
    * [checkpoints](#omega_vision.core.memory.SymbolicMemory.checkpoints)
    * [restore](#omega_vision.core.memory.SymbolicMemory.restore)
  * [SingleWriter](#omega_vision.core.memory.SingleWriter)
    * [\_\_init\_\_](#omega_vision.core.memory.SingleWriter.__init__)
    * [commit](#omega_vision.core.memory.SingleWriter.commit)
    * [commit\_residual](#omega_vision.core.memory.SingleWriter.commit_residual)
    * [accrue\_evidence](#omega_vision.core.memory.SingleWriter.accrue_evidence)
    * [apply\_evidence](#omega_vision.core.memory.SingleWriter.apply_evidence)
    * [tombstone](#omega_vision.core.memory.SingleWriter.tombstone)
    * [demote](#omega_vision.core.memory.SingleWriter.demote)
    * [merge\_identities](#omega_vision.core.memory.SingleWriter.merge_identities)
    * [split\_identity](#omega_vision.core.memory.SingleWriter.split_identity)
    * [reverse\_identity\_decision](#omega_vision.core.memory.SingleWriter.reverse_identity_decision)
* [omega\_vision.core.models](#omega_vision.core.models)
  * [PHASE2\_SCHEMA\_VERSION](#omega_vision.core.models.PHASE2_SCHEMA_VERSION)
  * [deterministic\_identifier](#omega_vision.core.models.deterministic_identifier)
  * [ExecutionMode](#omega_vision.core.models.ExecutionMode)
    * [PROLOG](#omega_vision.core.models.ExecutionMode.PROLOG)
    * [GPT](#omega_vision.core.models.ExecutionMode.GPT)
    * [PYTHON](#omega_vision.core.models.ExecutionMode.PYTHON)
  * [ResidualDisposition](#omega_vision.core.models.ResidualDisposition)
    * [ABSORBED](#omega_vision.core.models.ResidualDisposition.ABSORBED)
    * [PROVISIONAL](#omega_vision.core.models.ResidualDisposition.PROVISIONAL)
    * [COMMIT\_REQUEST](#omega_vision.core.models.ResidualDisposition.COMMIT_REQUEST)
  * [EvidencePolarity](#omega_vision.core.models.EvidencePolarity)
    * [SUPPORTS](#omega_vision.core.models.EvidencePolarity.SUPPORTS)
    * [CONTRADICTS](#omega_vision.core.models.EvidencePolarity.CONTRADICTS)
  * [IdentityDecision](#omega_vision.core.models.IdentityDecision)
    * [PROPOSED](#omega_vision.core.models.IdentityDecision.PROPOSED)
    * [ACCEPTED](#omega_vision.core.models.IdentityDecision.ACCEPTED)
    * [REJECTED](#omega_vision.core.models.IdentityDecision.REJECTED)
    * [REVERSED](#omega_vision.core.models.IdentityDecision.REVERSED)
  * [ProvenanceRef](#omega_vision.core.models.ProvenanceRef)
    * [source\_id](#omega_vision.core.models.ProvenanceRef.source_id)
    * [provider](#omega_vision.core.models.ProvenanceRef.provider)
    * [action\_tree\_node](#omega_vision.core.models.ProvenanceRef.action_tree_node)
    * [artifact\_id](#omega_vision.core.models.ProvenanceRef.artifact_id)
    * [sequence](#omega_vision.core.models.ProvenanceRef.sequence)
    * [metadata](#omega_vision.core.models.ProvenanceRef.metadata)
    * [schema\_version](#omega_vision.core.models.ProvenanceRef.schema_version)
    * [create](#omega_vision.core.models.ProvenanceRef.create)
  * [ArtifactRef](#omega_vision.core.models.ArtifactRef)
    * [artifact\_id](#omega_vision.core.models.ArtifactRef.artifact_id)
    * [artifact\_type](#omega_vision.core.models.ArtifactRef.artifact_type)
    * [uri](#omega_vision.core.models.ArtifactRef.uri)
    * [content\_hash](#omega_vision.core.models.ArtifactRef.content_hash)
    * [media\_type](#omega_vision.core.models.ArtifactRef.media_type)
    * [provenance](#omega_vision.core.models.ArtifactRef.provenance)
    * [schema\_version](#omega_vision.core.models.ArtifactRef.schema_version)
    * [create](#omega_vision.core.models.ArtifactRef.create)
  * [TurtleProgramRef](#omega_vision.core.models.TurtleProgramRef)
    * [artifact](#omega_vision.core.models.TurtleProgramRef.artifact)
    * [language](#omega_vision.core.models.TurtleProgramRef.language)
    * [entrypoint](#omega_vision.core.models.TurtleProgramRef.entrypoint)
    * [fit\_score](#omega_vision.core.models.TurtleProgramRef.fit_score)
    * [distance](#omega_vision.core.models.TurtleProgramRef.distance)
    * [residual\_score](#omega_vision.core.models.TurtleProgramRef.residual_score)
    * [description\_length](#omega_vision.core.models.TurtleProgramRef.description_length)
    * [schema\_version](#omega_vision.core.models.TurtleProgramRef.schema_version)
  * [InstanceParameters](#omega_vision.core.models.InstanceParameters)
    * [position](#omega_vision.core.models.InstanceParameters.position)
    * [orientation](#omega_vision.core.models.InstanceParameters.orientation)
    * [scale](#omega_vision.core.models.InstanceParameters.scale)
    * [appearance](#omega_vision.core.models.InstanceParameters.appearance)
    * [supported\_transformations](#omega_vision.core.models.InstanceParameters.supported_transformations)
    * [reflection](#omega_vision.core.models.InstanceParameters.reflection)
    * [visibility](#omega_vision.core.models.InstanceParameters.visibility)
    * [noise\_score](#omega_vision.core.models.InstanceParameters.noise_score)
    * [geometry](#omega_vision.core.models.InstanceParameters.geometry)
    * [topology](#omega_vision.core.models.InstanceParameters.topology)
    * [relationships](#omega_vision.core.models.InstanceParameters.relationships)
    * [schema\_version](#omega_vision.core.models.InstanceParameters.schema_version)
  * [EvidenceRecord](#omega_vision.core.models.EvidenceRecord)
    * [evidence\_id](#omega_vision.core.models.EvidenceRecord.evidence_id)
    * [subject\_id](#omega_vision.core.models.EvidenceRecord.subject_id)
    * [polarity](#omega_vision.core.models.EvidenceRecord.polarity)
    * [source](#omega_vision.core.models.EvidenceRecord.source)
    * [weight](#omega_vision.core.models.EvidenceRecord.weight)
    * [detail](#omega_vision.core.models.EvidenceRecord.detail)
    * [created\_sequence](#omega_vision.core.models.EvidenceRecord.created_sequence)
    * [schema\_version](#omega_vision.core.models.EvidenceRecord.schema_version)
    * [create](#omega_vision.core.models.EvidenceRecord.create)
  * [Observation](#omega_vision.core.models.Observation)
    * [observation\_id](#omega_vision.core.models.Observation.observation_id)
    * [source\_modality](#omega_vision.core.models.Observation.source_modality)
    * [artifacts](#omega_vision.core.models.Observation.artifacts)
    * [dimensions](#omega_vision.core.models.Observation.dimensions)
    * [coordinate\_contract](#omega_vision.core.models.Observation.coordinate_contract)
    * [candidate\_object\_ids](#omega_vision.core.models.Observation.candidate_object_ids)
    * [action\_tree\_node](#omega_vision.core.models.Observation.action_tree_node)
    * [provenance](#omega_vision.core.models.Observation.provenance)
    * [schema\_version](#omega_vision.core.models.Observation.schema_version)
    * [create](#omega_vision.core.models.Observation.create)
  * [MatchProposal](#omega_vision.core.models.MatchProposal)
    * [proposal\_id](#omega_vision.core.models.MatchProposal.proposal_id)
    * [candidate\_id](#omega_vision.core.models.MatchProposal.candidate_id)
    * [stored\_identity\_id](#omega_vision.core.models.MatchProposal.stored_identity_id)
    * [matched\_properties](#omega_vision.core.models.MatchProposal.matched_properties)
    * [changed\_properties](#omega_vision.core.models.MatchProposal.changed_properties)
    * [allowed\_transformations](#omega_vision.core.models.MatchProposal.allowed_transformations)
    * [similarity](#omega_vision.core.models.MatchProposal.similarity)
    * [retrieval\_score](#omega_vision.core.models.MatchProposal.retrieval_score)
    * [retrieval\_source](#omega_vision.core.models.MatchProposal.retrieval_source)
    * [probability](#omega_vision.core.models.MatchProposal.probability)
    * [probability\_source](#omega_vision.core.models.MatchProposal.probability_source)
    * [evidence\_ids](#omega_vision.core.models.MatchProposal.evidence_ids)
    * [provenance](#omega_vision.core.models.MatchProposal.provenance)
    * [schema\_version](#omega_vision.core.models.MatchProposal.schema_version)
    * [\_\_post\_init\_\_](#omega_vision.core.models.MatchProposal.__post_init__)
    * [create](#omega_vision.core.models.MatchProposal.create)
  * [MergeDecision](#omega_vision.core.models.MergeDecision)
    * [decision\_id](#omega_vision.core.models.MergeDecision.decision_id)
    * [identity\_ids](#omega_vision.core.models.MergeDecision.identity_ids)
    * [resulting\_identity\_id](#omega_vision.core.models.MergeDecision.resulting_identity_id)
    * [status](#omega_vision.core.models.MergeDecision.status)
    * [evidence\_ids](#omega_vision.core.models.MergeDecision.evidence_ids)
    * [provenance](#omega_vision.core.models.MergeDecision.provenance)
    * [schema\_version](#omega_vision.core.models.MergeDecision.schema_version)
    * [create](#omega_vision.core.models.MergeDecision.create)
  * [SplitDecision](#omega_vision.core.models.SplitDecision)
    * [decision\_id](#omega_vision.core.models.SplitDecision.decision_id)
    * [source\_identity\_id](#omega_vision.core.models.SplitDecision.source_identity_id)
    * [resulting\_identity\_ids](#omega_vision.core.models.SplitDecision.resulting_identity_ids)
    * [status](#omega_vision.core.models.SplitDecision.status)
    * [evidence\_ids](#omega_vision.core.models.SplitDecision.evidence_ids)
    * [provenance](#omega_vision.core.models.SplitDecision.provenance)
    * [schema\_version](#omega_vision.core.models.SplitDecision.schema_version)
    * [create](#omega_vision.core.models.SplitDecision.create)
  * [IdentityMemoryCheckpoint](#omega_vision.core.models.IdentityMemoryCheckpoint)
    * [checkpoint\_id](#omega_vision.core.models.IdentityMemoryCheckpoint.checkpoint_id)
    * [sequence](#omega_vision.core.models.IdentityMemoryCheckpoint.sequence)
    * [event](#omega_vision.core.models.IdentityMemoryCheckpoint.event)
    * [reference\_id](#omega_vision.core.models.IdentityMemoryCheckpoint.reference_id)
    * [parent\_checkpoint\_id](#omega_vision.core.models.IdentityMemoryCheckpoint.parent_checkpoint_id)
    * [atoms](#omega_vision.core.models.IdentityMemoryCheckpoint.atoms)
    * [evidence](#omega_vision.core.models.IdentityMemoryCheckpoint.evidence)
    * [merge\_decisions](#omega_vision.core.models.IdentityMemoryCheckpoint.merge_decisions)
    * [split\_decisions](#omega_vision.core.models.IdentityMemoryCheckpoint.split_decisions)
    * [decision\_snapshots](#omega_vision.core.models.IdentityMemoryCheckpoint.decision_snapshots)
    * [confidence\_history](#omega_vision.core.models.IdentityMemoryCheckpoint.confidence_history)
    * [schema\_version](#omega_vision.core.models.IdentityMemoryCheckpoint.schema_version)
    * [create](#omega_vision.core.models.IdentityMemoryCheckpoint.create)
    * [as\_compaction\_root](#omega_vision.core.models.IdentityMemoryCheckpoint.as_compaction_root)
  * [RecognitionAccount](#omega_vision.core.models.RecognitionAccount)
    * [account\_id](#omega_vision.core.models.RecognitionAccount.account_id)
    * [candidate\_id](#omega_vision.core.models.RecognitionAccount.candidate_id)
    * [stored\_identity\_id](#omega_vision.core.models.RecognitionAccount.stored_identity_id)
    * [matched\_properties](#omega_vision.core.models.RecognitionAccount.matched_properties)
    * [changed\_properties](#omega_vision.core.models.RecognitionAccount.changed_properties)
    * [allowed\_transformations](#omega_vision.core.models.RecognitionAccount.allowed_transformations)
    * [turtle\_reconstruction\_fit](#omega_vision.core.models.RecognitionAccount.turtle_reconstruction_fit)
    * [residual\_score](#omega_vision.core.models.RecognitionAccount.residual_score)
    * [supporting\_evidence\_ids](#omega_vision.core.models.RecognitionAccount.supporting_evidence_ids)
    * [contradicting\_evidence\_ids](#omega_vision.core.models.RecognitionAccount.contradicting_evidence_ids)
    * [rival\_proposal\_ids](#omega_vision.core.models.RecognitionAccount.rival_proposal_ids)
    * [calibrated\_confidence](#omega_vision.core.models.RecognitionAccount.calibrated_confidence)
    * [decision\_confidence](#omega_vision.core.models.RecognitionAccount.decision_confidence)
    * [decision\_outcome](#omega_vision.core.models.RecognitionAccount.decision_outcome)
    * [decision\_source](#omega_vision.core.models.RecognitionAccount.decision_source)
    * [provenance](#omega_vision.core.models.RecognitionAccount.provenance)
    * [schema\_version](#omega_vision.core.models.RecognitionAccount.schema_version)
    * [create](#omega_vision.core.models.RecognitionAccount.create)
  * [ObjectChange](#omega_vision.core.models.ObjectChange)
    * [change\_id](#omega_vision.core.models.ObjectChange.change_id)
    * [kind](#omega_vision.core.models.ObjectChange.kind)
    * [before\_identity\_ids](#omega_vision.core.models.ObjectChange.before_identity_ids)
    * [after\_candidate\_ids](#omega_vision.core.models.ObjectChange.after_candidate_ids)
    * [properties](#omega_vision.core.models.ObjectChange.properties)
    * [evidence\_ids](#omega_vision.core.models.ObjectChange.evidence_ids)
    * [provenance](#omega_vision.core.models.ObjectChange.provenance)
    * [schema\_version](#omega_vision.core.models.ObjectChange.schema_version)
    * [create](#omega_vision.core.models.ObjectChange.create)
  * [EncounterRecord](#omega_vision.core.models.EncounterRecord)
    * [encounter\_id](#omega_vision.core.models.EncounterRecord.encounter_id)
    * [observation\_id](#omega_vision.core.models.EncounterRecord.observation_id)
    * [action\_tree\_node](#omega_vision.core.models.EncounterRecord.action_tree_node)
    * [object\_identity\_id](#omega_vision.core.models.EncounterRecord.object_identity_id)
    * [candidate\_identity\_id](#omega_vision.core.models.EncounterRecord.candidate_identity_id)
    * [instance](#omega_vision.core.models.EncounterRecord.instance)
    * [matched\_properties](#omega_vision.core.models.EncounterRecord.matched_properties)
    * [changed\_properties](#omega_vision.core.models.EncounterRecord.changed_properties)
    * [turtle\_programs](#omega_vision.core.models.EncounterRecord.turtle_programs)
    * [reconstruction\_artifacts](#omega_vision.core.models.EncounterRecord.reconstruction_artifacts)
    * [residual\_ids](#omega_vision.core.models.EncounterRecord.residual_ids)
    * [confidence](#omega_vision.core.models.EncounterRecord.confidence)
    * [evidence\_ids](#omega_vision.core.models.EncounterRecord.evidence_ids)
    * [previous\_encounter\_id](#omega_vision.core.models.EncounterRecord.previous_encounter_id)
    * [next\_encounter\_id](#omega_vision.core.models.EncounterRecord.next_encounter_id)
    * [provenance](#omega_vision.core.models.EncounterRecord.provenance)
    * [deterministic\_hash](#omega_vision.core.models.EncounterRecord.deterministic_hash)
    * [schema\_version](#omega_vision.core.models.EncounterRecord.schema_version)
    * [create](#omega_vision.core.models.EncounterRecord.create)
  * [NormalizedResult](#omega_vision.core.models.NormalizedResult)
    * [value](#omega_vision.core.models.NormalizedResult.value)
    * [mode](#omega_vision.core.models.NormalizedResult.mode)
    * [source\_refs](#omega_vision.core.models.NormalizedResult.source_refs)
    * [evidence](#omega_vision.core.models.NormalizedResult.evidence)
    * [metadata](#omega_vision.core.models.NormalizedResult.metadata)
  * [CandidateObject](#omega_vision.core.models.CandidateObject)
    * [candidate\_id](#omega_vision.core.models.CandidateObject.candidate_id)
    * [observation\_id](#omega_vision.core.models.CandidateObject.observation_id)
    * [domain](#omega_vision.core.models.CandidateObject.domain)
    * [provider](#omega_vision.core.models.CandidateObject.provider)
    * [region\_ref](#omega_vision.core.models.CandidateObject.region_ref)
    * [provenance](#omega_vision.core.models.CandidateObject.provenance)
    * [part](#omega_vision.core.models.CandidateObject.part)
  * [ResidualCandidate](#omega_vision.core.models.ResidualCandidate)
    * [residual\_id](#omega_vision.core.models.ResidualCandidate.residual_id)
    * [source\_candidate\_id](#omega_vision.core.models.ResidualCandidate.source_candidate_id)
    * [disposition](#omega_vision.core.models.ResidualCandidate.disposition)
    * [residual\_length](#omega_vision.core.models.ResidualCandidate.residual_length)
    * [structured](#omega_vision.core.models.ResidualCandidate.structured)
    * [recurrence\_count](#omega_vision.core.models.ResidualCandidate.recurrence_count)
    * [prediction\_gain](#omega_vision.core.models.ResidualCandidate.prediction_gain)
    * [provenance](#omega_vision.core.models.ResidualCandidate.provenance)
    * [create](#omega_vision.core.models.ResidualCandidate.create)
  * [CommittedAtom](#omega_vision.core.models.CommittedAtom)
    * [handle](#omega_vision.core.models.CommittedAtom.handle)
    * [atom\_type](#omega_vision.core.models.CommittedAtom.atom_type)
    * [payload](#omega_vision.core.models.CommittedAtom.payload)
    * [confidence](#omega_vision.core.models.CommittedAtom.confidence)
    * [provenance](#omega_vision.core.models.CommittedAtom.provenance)
    * [lifecycle\_state](#omega_vision.core.models.CommittedAtom.lifecycle_state)
  * [ConfidenceHistoryRecord](#omega_vision.core.models.ConfidenceHistoryRecord)
    * [sequence](#omega_vision.core.models.ConfidenceHistoryRecord.sequence)
    * [handle](#omega_vision.core.models.ConfidenceHistoryRecord.handle)
    * [confidence](#omega_vision.core.models.ConfidenceHistoryRecord.confidence)
    * [lifecycle\_state](#omega_vision.core.models.ConfidenceHistoryRecord.lifecycle_state)
    * [event](#omega_vision.core.models.ConfidenceHistoryRecord.event)
    * [reference\_id](#omega_vision.core.models.ConfidenceHistoryRecord.reference_id)
  * [TransitionRule](#omega_vision.core.models.TransitionRule)
    * [rule\_id](#omega_vision.core.models.TransitionRule.rule_id)
    * [preconditions](#omega_vision.core.models.TransitionRule.preconditions)
    * [action\_or\_event](#omega_vision.core.models.TransitionRule.action_or_event)
    * [predicted\_effects](#omega_vision.core.models.TransitionRule.predicted_effects)
    * [provenance](#omega_vision.core.models.TransitionRule.provenance)
    * [assumptions](#omega_vision.core.models.TransitionRule.assumptions)
    * [critiques](#omega_vision.core.models.TransitionRule.critiques)
    * [supporting\_evidence\_ids](#omega_vision.core.models.TransitionRule.supporting_evidence_ids)
    * [contradicting\_evidence\_ids](#omega_vision.core.models.TransitionRule.contradicting_evidence_ids)
    * [rival\_rule\_ids](#omega_vision.core.models.TransitionRule.rival_rule_ids)
    * [bootstrap\_probability](#omega_vision.core.models.TransitionRule.bootstrap_probability)
    * [calibrated\_probability](#omega_vision.core.models.TransitionRule.calibrated_probability)
    * [probability\_source](#omega_vision.core.models.TransitionRule.probability_source)
    * [coverage](#omega_vision.core.models.TransitionRule.coverage)
    * [applicability\_precision](#omega_vision.core.models.TransitionRule.applicability_precision)
    * [prediction\_attempts](#omega_vision.core.models.TransitionRule.prediction_attempts)
    * [prediction\_successes](#omega_vision.core.models.TransitionRule.prediction_successes)
    * [prediction\_score\_total](#omega_vision.core.models.TransitionRule.prediction_score_total)
    * [prediction\_history](#omega_vision.core.models.TransitionRule.prediction_history)
  * [ActionRecommendation](#omega_vision.core.models.ActionRecommendation)
    * [recommendation\_id](#omega_vision.core.models.ActionRecommendation.recommendation_id)
    * [rule\_id](#omega_vision.core.models.ActionRecommendation.rule_id)
    * [source\_state\_id](#omega_vision.core.models.ActionRecommendation.source_state_id)
    * [recommended\_action](#omega_vision.core.models.ActionRecommendation.recommended_action)
    * [attempted\_action](#omega_vision.core.models.ActionRecommendation.attempted_action)
    * [created\_sequence](#omega_vision.core.models.ActionRecommendation.created_sequence)
    * [rival\_rule\_ids](#omega_vision.core.models.ActionRecommendation.rival_rule_ids)
    * [available\_evidence\_ids](#omega_vision.core.models.ActionRecommendation.available_evidence_ids)
    * [assumptions](#omega_vision.core.models.ActionRecommendation.assumptions)
    * [critiques](#omega_vision.core.models.ActionRecommendation.critiques)
    * [probability](#omega_vision.core.models.ActionRecommendation.probability)
    * [probability\_source](#omega_vision.core.models.ActionRecommendation.probability_source)
    * [prediction\_id](#omega_vision.core.models.ActionRecommendation.prediction_id)
    * [schema\_version](#omega_vision.core.models.ActionRecommendation.schema_version)
    * [create](#omega_vision.core.models.ActionRecommendation.create)
  * [PredictionRecord](#omega_vision.core.models.PredictionRecord)
    * [prediction\_id](#omega_vision.core.models.PredictionRecord.prediction_id)
    * [rule\_id](#omega_vision.core.models.PredictionRecord.rule_id)
    * [source\_state\_id](#omega_vision.core.models.PredictionRecord.source_state_id)
    * [predicted\_effects](#omega_vision.core.models.PredictionRecord.predicted_effects)
    * [created\_sequence](#omega_vision.core.models.PredictionRecord.created_sequence)
    * [available\_evidence\_ids](#omega_vision.core.models.PredictionRecord.available_evidence_ids)
    * [rule\_assumptions](#omega_vision.core.models.PredictionRecord.rule_assumptions)
    * [rule\_critiques](#omega_vision.core.models.PredictionRecord.rule_critiques)
    * [rule\_probability](#omega_vision.core.models.PredictionRecord.rule_probability)
    * [rule\_probability\_source](#omega_vision.core.models.PredictionRecord.rule_probability_source)
    * [outcome\_sequence](#omega_vision.core.models.PredictionRecord.outcome_sequence)
    * [outcome](#omega_vision.core.models.PredictionRecord.outcome)
    * [grade](#omega_vision.core.models.PredictionRecord.grade)
  * [PredictionGradeRecord](#omega_vision.core.models.PredictionGradeRecord)
    * [prediction\_id](#omega_vision.core.models.PredictionGradeRecord.prediction_id)
    * [rule\_id](#omega_vision.core.models.PredictionGradeRecord.rule_id)
    * [outcome\_sequence](#omega_vision.core.models.PredictionGradeRecord.outcome_sequence)
    * [outcome](#omega_vision.core.models.PredictionGradeRecord.outcome)
    * [grade](#omega_vision.core.models.PredictionGradeRecord.grade)
    * [status](#omega_vision.core.models.PredictionGradeRecord.status)
    * [evidence](#omega_vision.core.models.PredictionGradeRecord.evidence)
    * [evidence\_record\_ids](#omega_vision.core.models.PredictionGradeRecord.evidence_record_ids)
    * [prior\_probability](#omega_vision.core.models.PredictionGradeRecord.prior_probability)
    * [calibrated\_probability](#omega_vision.core.models.PredictionGradeRecord.calibrated_probability)
    * [schema\_version](#omega_vision.core.models.PredictionGradeRecord.schema_version)
  * [ArtifactProviderProtocol](#omega_vision.core.models.ArtifactProviderProtocol)
    * [get\_candidate\_part](#omega_vision.core.models.ArtifactProviderProtocol.get_candidate_part)
* [omega\_vision.core.prediction](#omega_vision.core.prediction)
  * [RuleStore](#omega_vision.core.prediction.RuleStore)
    * [\_\_init\_\_](#omega_vision.core.prediction.RuleStore.__init__)
    * [store](#omega_vision.core.prediction.RuleStore.store)
    * [get](#omega_vision.core.prediction.RuleStore.get)
    * [rules](#omega_vision.core.prediction.RuleStore.rules)
    * [record\_prediction\_grade](#omega_vision.core.prediction.RuleStore.record_prediction_grade)
    * [applicable](#omega_vision.core.prediction.RuleStore.applicable)
    * [apply](#omega_vision.core.prediction.RuleStore.apply)
  * [PredictionLedger](#omega_vision.core.prediction.PredictionLedger)
    * [\_\_init\_\_](#omega_vision.core.prediction.PredictionLedger.__init__)
    * [record](#omega_vision.core.prediction.PredictionLedger.record)
    * [grade](#omega_vision.core.prediction.PredictionLedger.grade)
    * [get](#omega_vision.core.prediction.PredictionLedger.get)
    * [records](#omega_vision.core.prediction.PredictionLedger.records)
* [omega\_vision.core.recognition](#omega_vision.core.recognition)
  * [PartialVisibilityCompletion](#omega_vision.core.recognition.PartialVisibilityCompletion)
    * [candidate\_id](#omega_vision.core.recognition.PartialVisibilityCompletion.candidate_id)
    * [stored\_identity\_id](#omega_vision.core.recognition.PartialVisibilityCompletion.stored_identity_id)
    * [observed](#omega_vision.core.recognition.PartialVisibilityCompletion.observed)
    * [completed](#omega_vision.core.recognition.PartialVisibilityCompletion.completed)
    * [inferred\_fields](#omega_vision.core.recognition.PartialVisibilityCompletion.inferred_fields)
    * [proposal\_id](#omega_vision.core.recognition.PartialVisibilityCompletion.proposal_id)
    * [evidence\_ids](#omega_vision.core.recognition.PartialVisibilityCompletion.evidence_ids)
  * [InstanceMatcher](#omega_vision.core.recognition.InstanceMatcher)
    * [change\_transformation](#omega_vision.core.recognition.InstanceMatcher.change_transformation)
    * [compare](#omega_vision.core.recognition.InstanceMatcher.compare)
    * [proposals](#omega_vision.core.recognition.InstanceMatcher.proposals)
    * [recognition\_account](#omega_vision.core.recognition.InstanceMatcher.recognition_account)
  * [RecognitionSession](#omega_vision.core.recognition.RecognitionSession)
    * [\_\_init\_\_](#omega_vision.core.recognition.RecognitionSession.__init__)
    * [latest\_known\_instances](#omega_vision.core.recognition.RecognitionSession.latest_known_instances)
    * [complete\_partial](#omega_vision.core.recognition.RecognitionSession.complete_partial)
    * [propose](#omega_vision.core.recognition.RecognitionSession.propose)
    * [unresolved\_account](#omega_vision.core.recognition.RecognitionSession.unresolved_account)
  * [CorrespondenceEvidenceBuilder](#omega_vision.core.recognition.CorrespondenceEvidenceBuilder)
    * [build](#omega_vision.core.recognition.CorrespondenceEvidenceBuilder.build)
  * [EncounterChangeSession](#omega_vision.core.recognition.EncounterChangeSession)
    * [\_\_init\_\_](#omega_vision.core.recognition.EncounterChangeSession.__init__)
    * [detect](#omega_vision.core.recognition.EncounterChangeSession.detect)
  * [StructuralCorrespondenceInferer](#omega_vision.core.recognition.StructuralCorrespondenceInferer)
    * [infer](#omega_vision.core.recognition.StructuralCorrespondenceInferer.infer)
  * [ResidualAnalyzer](#omega_vision.core.recognition.ResidualAnalyzer)
    * [\_\_init\_\_](#omega_vision.core.recognition.ResidualAnalyzer.__init__)
    * [from\_proposal](#omega_vision.core.recognition.ResidualAnalyzer.from_proposal)
  * [TurtleReconstructionEvidenceBuilder](#omega_vision.core.recognition.TurtleReconstructionEvidenceBuilder)
    * [build](#omega_vision.core.recognition.TurtleReconstructionEvidenceBuilder.build)
  * [ChangeDetector](#omega_vision.core.recognition.ChangeDetector)
    * [PROPERTY\_KINDS](#omega_vision.core.recognition.ChangeDetector.PROPERTY_KINDS)
    * [detect](#omega_vision.core.recognition.ChangeDetector.detect)
  * [RegistryCorrespondenceAuthority](#omega_vision.core.recognition.RegistryCorrespondenceAuthority)
    * [\_\_init\_\_](#omega_vision.core.recognition.RegistryCorrespondenceAuthority.__init__)
    * [accept](#omega_vision.core.recognition.RegistryCorrespondenceAuthority.accept)
    * [reject](#omega_vision.core.recognition.RegistryCorrespondenceAuthority.reject)
    * [reverse](#omega_vision.core.recognition.RegistryCorrespondenceAuthority.reverse)
* [omega\_vision.core.store](#omega_vision.core.store)
  * [SemanticStoreBackend](#omega_vision.core.store.SemanticStoreBackend)
    * [write\_once](#omega_vision.core.store.SemanticStoreBackend.write_once)
    * [get](#omega_vision.core.store.SemanticStoreBackend.get)
    * [values](#omega_vision.core.store.SemanticStoreBackend.values)
  * [InMemorySemanticBackend](#omega_vision.core.store.InMemorySemanticBackend)
    * [\_\_init\_\_](#omega_vision.core.store.InMemorySemanticBackend.__init__)
    * [write\_once](#omega_vision.core.store.InMemorySemanticBackend.write_once)
    * [get](#omega_vision.core.store.InMemorySemanticBackend.get)
    * [values](#omega_vision.core.store.InMemorySemanticBackend.values)
  * [ArtifactIndex](#omega_vision.core.store.ArtifactIndex)
    * [\_\_init\_\_](#omega_vision.core.store.ArtifactIndex.__init__)
    * [register](#omega_vision.core.store.ArtifactIndex.register)
    * [get](#omega_vision.core.store.ArtifactIndex.get)
    * [by\_type](#omega_vision.core.store.ArtifactIndex.by_type)
  * [SymbolicStore](#omega_vision.core.store.SymbolicStore)
    * [\_\_init\_\_](#omega_vision.core.store.SymbolicStore.__init__)
    * [put\_observation](#omega_vision.core.store.SymbolicStore.put_observation)
    * [put\_encounter](#omega_vision.core.store.SymbolicStore.put_encounter)
    * [put\_recognition](#omega_vision.core.store.SymbolicStore.put_recognition)
    * [put\_match\_proposal](#omega_vision.core.store.SymbolicStore.put_match_proposal)
    * [put\_evidence](#omega_vision.core.store.SymbolicStore.put_evidence)
    * [put\_object\_change](#omega_vision.core.store.SymbolicStore.put_object_change)
    * [put\_residual](#omega_vision.core.store.SymbolicStore.put_residual)
    * [put\_artifact](#omega_vision.core.store.SymbolicStore.put_artifact)
    * [put\_turtle](#omega_vision.core.store.SymbolicStore.put_turtle)
    * [put\_atom](#omega_vision.core.store.SymbolicStore.put_atom)
    * [put\_confidence\_history](#omega_vision.core.store.SymbolicStore.put_confidence_history)
    * [put\_identity\_checkpoint](#omega_vision.core.store.SymbolicStore.put_identity_checkpoint)
    * [put\_recognition\_calibration](#omega_vision.core.store.SymbolicStore.put_recognition_calibration)
    * [restore\_identity\_memory](#omega_vision.core.store.SymbolicStore.restore_identity_memory)
    * [compacted\_snapshot](#omega_vision.core.store.SymbolicStore.compacted_snapshot)
    * [put\_prediction](#omega_vision.core.store.SymbolicStore.put_prediction)
    * [put\_transition\_rule](#omega_vision.core.store.SymbolicStore.put_transition_rule)
    * [put\_action\_recommendation](#omega_vision.core.store.SymbolicStore.put_action_recommendation)
    * [put\_prediction\_grade](#omega_vision.core.store.SymbolicStore.put_prediction_grade)
    * [get](#omega_vision.core.store.SymbolicStore.get)
    * [values](#omega_vision.core.store.SymbolicStore.values)
    * [SNAPSHOT\_NAMESPACES](#omega_vision.core.store.SymbolicStore.SNAPSHOT_NAMESPACES)
    * [snapshot](#omega_vision.core.store.SymbolicStore.snapshot)
    * [replay](#omega_vision.core.store.SymbolicStore.replay)
    * [hydrate](#omega_vision.core.store.SymbolicStore.hydrate)
* [omega\_vision.environments.environment\_fixtures](#omega_vision.environments.environment_fixtures)
  * [EnvironmentProgressionFixtures](#omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures)
    * [rendered\_arcade](#omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures.rendered_arcade)
    * [fixed\_camera](#omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures.fixed_camera)
    * [top\_down\_manipulation](#omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures.top_down_manipulation)
    * [all](#omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures.all)
  * [rendered\_arcade\_fixtures](#omega_vision.environments.environment_fixtures.rendered_arcade_fixtures)
  * [fixed\_camera\_physics\_fixtures](#omega_vision.environments.environment_fixtures.fixed_camera_physics_fixtures)
  * [top\_down\_manipulation\_fixtures](#omega_vision.environments.environment_fixtures.top_down_manipulation_fixtures)
  * [environment\_progression\_fixtures](#omega_vision.environments.environment_fixtures.environment_progression_fixtures)
* [omega\_vision.evaluation.acceptance](#omega_vision.evaluation.acceptance)
  * [AcceptanceReport](#omega_vision.evaluation.acceptance.AcceptanceReport)
    * [accepted](#omega_vision.evaluation.acceptance.AcceptanceReport.accepted)
    * [checks](#omega_vision.evaluation.acceptance.AcceptanceReport.checks)
    * [evidence](#omega_vision.evaluation.acceptance.AcceptanceReport.evidence)
    * [to\_json](#omega_vision.evaluation.acceptance.AcceptanceReport.to_json)
    * [to\_markdown](#omega_vision.evaluation.acceptance.AcceptanceReport.to_markdown)
  * [build\_acceptance\_report](#omega_vision.evaluation.acceptance.build_acceptance_report)
  * [write\_acceptance\_report](#omega_vision.evaluation.acceptance.write_acceptance_report)
* [omega\_vision.evaluation.benchmark](#omega_vision.evaluation.benchmark)
  * [PerceptionFixture](#omega_vision.evaluation.benchmark.PerceptionFixture)
    * [fixture\_id](#omega_vision.evaluation.benchmark.PerceptionFixture.fixture_id)
    * [image](#omega_vision.evaluation.benchmark.PerceptionFixture.image)
    * [expected\_count](#omega_vision.evaluation.benchmark.PerceptionFixture.expected_count)
    * [degradation](#omega_vision.evaluation.benchmark.PerceptionFixture.degradation)
  * [PerceptionBenchmarkResult](#omega_vision.evaluation.benchmark.PerceptionBenchmarkResult)
    * [fixture\_id](#omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.fixture_id)
    * [expected\_count](#omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.expected_count)
    * [detected\_count](#omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.detected_count)
    * [count\_score](#omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.count_score)
    * [degradation](#omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.degradation)
  * [RasterPerturbationGenerator](#omega_vision.evaluation.benchmark.RasterPerturbationGenerator)
    * [\_\_init\_\_](#omega_vision.evaluation.benchmark.RasterPerturbationGenerator.__init__)
    * [noise](#omega_vision.evaluation.benchmark.RasterPerturbationGenerator.noise)
    * [occlude](#omega_vision.evaluation.benchmark.RasterPerturbationGenerator.occlude)
    * [partial\_occlusion\_dataset](#omega_vision.evaluation.benchmark.RasterPerturbationGenerator.partial_occlusion_dataset)
  * [PerceptionBenchmarkRunner](#omega_vision.evaluation.benchmark.PerceptionBenchmarkRunner)
    * [\_\_init\_\_](#omega_vision.evaluation.benchmark.PerceptionBenchmarkRunner.__init__)
    * [run](#omega_vision.evaluation.benchmark.PerceptionBenchmarkRunner.run)
  * [ProviderAblationRunner](#omega_vision.evaluation.benchmark.ProviderAblationRunner)
    * [\_\_init\_\_](#omega_vision.evaluation.benchmark.ProviderAblationRunner.__init__)
    * [run](#omega_vision.evaluation.benchmark.ProviderAblationRunner.run)
* [omega\_vision.evaluation.calibration](#omega_vision.evaluation.calibration)
  * [ReliabilityBin](#omega_vision.evaluation.calibration.ReliabilityBin)
    * [lower](#omega_vision.evaluation.calibration.ReliabilityBin.lower)
    * [upper](#omega_vision.evaluation.calibration.ReliabilityBin.upper)
    * [count](#omega_vision.evaluation.calibration.ReliabilityBin.count)
    * [mean\_confidence](#omega_vision.evaluation.calibration.ReliabilityBin.mean_confidence)
    * [acceptance\_rate](#omega_vision.evaluation.calibration.ReliabilityBin.acceptance_rate)
    * [brier\_score](#omega_vision.evaluation.calibration.ReliabilityBin.brier_score)
  * [RecognitionCalibrationReport](#omega_vision.evaluation.calibration.RecognitionCalibrationReport)
    * [scope](#omega_vision.evaluation.calibration.RecognitionCalibrationReport.scope)
    * [sample\_count](#omega_vision.evaluation.calibration.RecognitionCalibrationReport.sample_count)
    * [brier\_score](#omega_vision.evaluation.calibration.RecognitionCalibrationReport.brier_score)
    * [bins](#omega_vision.evaluation.calibration.RecognitionCalibrationReport.bins)
  * [CalibrationPoint](#omega_vision.evaluation.calibration.CalibrationPoint)
    * [upper\_confidence](#omega_vision.evaluation.calibration.CalibrationPoint.upper_confidence)
    * [probability](#omega_vision.evaluation.calibration.CalibrationPoint.probability)
    * [sample\_count](#omega_vision.evaluation.calibration.CalibrationPoint.sample_count)
  * [RecognitionCalibrationPolicy](#omega_vision.evaluation.calibration.RecognitionCalibrationPolicy)
    * [scope](#omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.scope)
    * [sample\_count](#omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.sample_count)
    * [points](#omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.points)
    * [method](#omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.method)
    * [\_\_post\_init\_\_](#omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.__post_init__)
    * [calibrate](#omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.calibrate)
    * [to\_dict](#omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.to_dict)
    * [from\_dict](#omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.from_dict)
  * [RecognitionCalibrator](#omega_vision.evaluation.calibration.RecognitionCalibrator)
    * [report](#omega_vision.evaluation.calibration.RecognitionCalibrator.report)
    * [fit](#omega_vision.evaluation.calibration.RecognitionCalibrator.fit)
    * [calibrated\_report](#omega_vision.evaluation.calibration.RecognitionCalibrator.calibrated_report)
* [omega\_vision.evaluation.recognition\_benchmark](#omega_vision.evaluation.recognition_benchmark)
  * [RecognitionFixture](#omega_vision.evaluation.recognition_benchmark.RecognitionFixture)
    * [fixture\_id](#omega_vision.evaluation.recognition_benchmark.RecognitionFixture.fixture_id)
    * [scope](#omega_vision.evaluation.recognition_benchmark.RecognitionFixture.scope)
    * [current](#omega_vision.evaluation.recognition_benchmark.RecognitionFixture.current)
    * [stored](#omega_vision.evaluation.recognition_benchmark.RecognitionFixture.stored)
    * [accepted\_identity\_id](#omega_vision.evaluation.recognition_benchmark.RecognitionFixture.accepted_identity_id)
  * [RecognitionBenchmarkResult](#omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkResult)
    * [fixture\_id](#omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkResult.fixture_id)
    * [scope](#omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkResult.scope)
    * [accounts](#omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkResult.accounts)
  * [RecognitionBenchmarkRunner](#omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkRunner)
    * [\_\_init\_\_](#omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkRunner.__init__)
    * [run](#omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkRunner.run)
    * [accounts](#omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkRunner.accounts)
* [omega\_vision.forms.forms](#omega_vision.forms.forms)
  * [FitResult](#omega_vision.forms.forms.FitResult)
    * [parameters](#omega_vision.forms.forms.FitResult.parameters)
    * [residual](#omega_vision.forms.forms.FitResult.residual)
  * [AbstractGenerativeForm](#omega_vision.forms.forms.AbstractGenerativeForm)
    * [domain](#omega_vision.forms.forms.AbstractGenerativeForm.domain)
    * [canonicalize](#omega_vision.forms.forms.AbstractGenerativeForm.canonicalize)
    * [render](#omega_vision.forms.forms.AbstractGenerativeForm.render)
    * [fit\_instance](#omega_vision.forms.forms.AbstractGenerativeForm.fit_instance)
    * [distance](#omega_vision.forms.forms.AbstractGenerativeForm.distance)
  * [GenerativeForm](#omega_vision.forms.forms.GenerativeForm)
    * [domain](#omega_vision.forms.forms.GenerativeForm.domain)
    * [\_\_init\_\_](#omega_vision.forms.forms.GenerativeForm.__init__)
    * [canonicalize](#omega_vision.forms.forms.GenerativeForm.canonicalize)
    * [render](#omega_vision.forms.forms.GenerativeForm.render)
    * [fit\_instance](#omega_vision.forms.forms.GenerativeForm.fit_instance)
    * [distance](#omega_vision.forms.forms.GenerativeForm.distance)
    * [description\_length](#omega_vision.forms.forms.GenerativeForm.description_length)
* [omega\_vision.runtime.capture](#omega_vision.runtime.capture)
  * [standard\_semantic\_grid\_observer](#omega_vision.runtime.capture.standard_semantic_grid_observer)
  * [SemanticGridCaptureObserver](#omega_vision.runtime.capture.SemanticGridCaptureObserver)
    * [\_\_init\_\_](#omega_vision.runtime.capture.SemanticGridCaptureObserver.__init__)
    * [authorization\_options](#omega_vision.runtime.capture.SemanticGridCaptureObserver.authorization_options)
    * [authorize\_candidate](#omega_vision.runtime.capture.SemanticGridCaptureObserver.authorize_candidate)
    * [reject\_candidate](#omega_vision.runtime.capture.SemanticGridCaptureObserver.reject_candidate)
    * [before\_action](#omega_vision.runtime.capture.SemanticGridCaptureObserver.before_action)
    * [on\_state\_captured](#omega_vision.runtime.capture.SemanticGridCaptureObserver.on_state_captured)
* [omega\_vision.runtime.catalog](#omega_vision.runtime.catalog)
  * [IdentityCatalogEntry](#omega_vision.runtime.catalog.IdentityCatalogEntry)
    * [identity\_id](#omega_vision.runtime.catalog.IdentityCatalogEntry.identity_id)
    * [instance](#omega_vision.runtime.catalog.IdentityCatalogEntry.instance)
    * [registry\_fact](#omega_vision.runtime.catalog.IdentityCatalogEntry.registry_fact)
    * [evidence](#omega_vision.runtime.catalog.IdentityCatalogEntry.evidence)
    * [provenance](#omega_vision.runtime.catalog.IdentityCatalogEntry.provenance)
  * [SemanticIdentityCatalog](#omega_vision.runtime.catalog.SemanticIdentityCatalog)
    * [entries](#omega_vision.runtime.catalog.SemanticIdentityCatalog.entries)
    * [source](#omega_vision.runtime.catalog.SemanticIdentityCatalog.source)
    * [schema\_version](#omega_vision.runtime.catalog.SemanticIdentityCatalog.schema_version)
    * [from\_store](#omega_vision.runtime.catalog.SemanticIdentityCatalog.from_store)
    * [to\_json](#omega_vision.runtime.catalog.SemanticIdentityCatalog.to_json)
    * [from\_json](#omega_vision.runtime.catalog.SemanticIdentityCatalog.from_json)
    * [import\_into](#omega_vision.runtime.catalog.SemanticIdentityCatalog.import_into)
    * [install\_registry](#omega_vision.runtime.catalog.SemanticIdentityCatalog.install_registry)
* [omega\_vision.runtime.integration](#omega_vision.runtime.integration)
  * [GAME\_OBJECT\_LEARNER\_SCHEMA\_VERSION](#omega_vision.runtime.integration.GAME_OBJECT_LEARNER_SCHEMA_VERSION)
  * [GameObjectLearnerPayload](#omega_vision.runtime.integration.GameObjectLearnerPayload)
    * [state\_id](#omega_vision.runtime.integration.GameObjectLearnerPayload.state_id)
    * [objects](#omega_vision.runtime.integration.GameObjectLearnerPayload.objects)
    * [correspondences](#omega_vision.runtime.integration.GameObjectLearnerPayload.correspondences)
    * [transitions](#omega_vision.runtime.integration.GameObjectLearnerPayload.transitions)
    * [provenance](#omega_vision.runtime.integration.GameObjectLearnerPayload.provenance)
    * [observation\_id](#omega_vision.runtime.integration.GameObjectLearnerPayload.observation_id)
    * [encounter\_ids](#omega_vision.runtime.integration.GameObjectLearnerPayload.encounter_ids)
    * [identity\_ids](#omega_vision.runtime.integration.GameObjectLearnerPayload.identity_ids)
    * [artifacts](#omega_vision.runtime.integration.GameObjectLearnerPayload.artifacts)
    * [evidence](#omega_vision.runtime.integration.GameObjectLearnerPayload.evidence)
    * [schema\_version](#omega_vision.runtime.integration.GameObjectLearnerPayload.schema_version)
    * [to\_dict](#omega_vision.runtime.integration.GameObjectLearnerPayload.to_dict)
    * [from\_dict](#omega_vision.runtime.integration.GameObjectLearnerPayload.from_dict)
  * [GameObjectLearnerResult](#omega_vision.runtime.integration.GameObjectLearnerResult)
    * [state\_id](#omega_vision.runtime.integration.GameObjectLearnerResult.state_id)
    * [learning\_step](#omega_vision.runtime.integration.GameObjectLearnerResult.learning_step)
    * [prediction\_id](#omega_vision.runtime.integration.GameObjectLearnerResult.prediction_id)
    * [recommendation](#omega_vision.runtime.integration.GameObjectLearnerResult.recommendation)
  * [IntegrationError](#omega_vision.runtime.integration.IntegrationError)
  * [GameObjectLearnerSchema](#omega_vision.runtime.integration.GameObjectLearnerSchema)
    * [required\_object\_fields](#omega_vision.runtime.integration.GameObjectLearnerSchema.required_object_fields)
    * [version](#omega_vision.runtime.integration.GameObjectLearnerSchema.version)
  * [IntegrationValidator](#omega_vision.runtime.integration.IntegrationValidator)
    * [\_\_init\_\_](#omega_vision.runtime.integration.IntegrationValidator.__init__)
    * [validate](#omega_vision.runtime.integration.IntegrationValidator.validate)
  * [Phase2LearnerPayloadBuilder](#omega_vision.runtime.integration.Phase2LearnerPayloadBuilder)
    * [\_\_init\_\_](#omega_vision.runtime.integration.Phase2LearnerPayloadBuilder.__init__)
    * [for\_observation](#omega_vision.runtime.integration.Phase2LearnerPayloadBuilder.for_observation)
  * [phase2\_transition\_analyzer](#omega_vision.runtime.integration.phase2_transition_analyzer)
  * [phase2\_transformation\_learner](#omega_vision.runtime.integration.phase2_transformation_learner)
  * [phase2\_rule\_inducer](#omega_vision.runtime.integration.phase2_rule_inducer)
  * [phase2\_rule\_ranker](#omega_vision.runtime.integration.phase2_rule_ranker)
  * [phase2\_rule\_executor](#omega_vision.runtime.integration.phase2_rule_executor)
  * [GameObjectLearnerPlugin](#omega_vision.runtime.integration.GameObjectLearnerPlugin)
    * [consume\_state](#omega_vision.runtime.integration.GameObjectLearnerPlugin.consume_state)
    * [consume\_transition](#omega_vision.runtime.integration.GameObjectLearnerPlugin.consume_transition)
    * [consume](#omega_vision.runtime.integration.GameObjectLearnerPlugin.consume)
  * [PipelineGameObjectLearnerPlugin](#omega_vision.runtime.integration.PipelineGameObjectLearnerPlugin)
    * [\_\_init\_\_](#omega_vision.runtime.integration.PipelineGameObjectLearnerPlugin.__init__)
    * [consume\_state](#omega_vision.runtime.integration.PipelineGameObjectLearnerPlugin.consume_state)
    * [consume\_transition](#omega_vision.runtime.integration.PipelineGameObjectLearnerPlugin.consume_transition)
* [omega\_vision.runtime.replay](#omega_vision.runtime.replay)
  * [SemanticRecordCodec](#omega_vision.runtime.replay.SemanticRecordCodec)
    * [decode](#omega_vision.runtime.replay.SemanticRecordCodec.decode)
    * [decode\_namespace](#omega_vision.runtime.replay.SemanticRecordCodec.decode_namespace)
  * [PrologSemanticBackend](#omega_vision.runtime.replay.PrologSemanticBackend)
    * [FACT](#omega_vision.runtime.replay.PrologSemanticBackend.FACT)
    * [\_\_init\_\_](#omega_vision.runtime.replay.PrologSemanticBackend.__init__)
    * [write\_once](#omega_vision.runtime.replay.PrologSemanticBackend.write_once)
    * [get](#omega_vision.runtime.replay.PrologSemanticBackend.get)
    * [values](#omega_vision.runtime.replay.PrologSemanticBackend.values)
  * [AtomSpaceTransport](#omega_vision.runtime.replay.AtomSpaceTransport)
    * [query](#omega_vision.runtime.replay.AtomSpaceTransport.query)
    * [assert\_expression](#omega_vision.runtime.replay.AtomSpaceTransport.assert_expression)
  * [MettaFileAtomSpaceTransport](#omega_vision.runtime.replay.MettaFileAtomSpaceTransport)
    * [HEADER](#omega_vision.runtime.replay.MettaFileAtomSpaceTransport.HEADER)
    * [\_\_init\_\_](#omega_vision.runtime.replay.MettaFileAtomSpaceTransport.__init__)
    * [query](#omega_vision.runtime.replay.MettaFileAtomSpaceTransport.query)
    * [assert\_expression](#omega_vision.runtime.replay.MettaFileAtomSpaceTransport.assert_expression)
  * [AtomSpaceSemanticBackend](#omega_vision.runtime.replay.AtomSpaceSemanticBackend)
    * [HEAD](#omega_vision.runtime.replay.AtomSpaceSemanticBackend.HEAD)
    * [\_\_init\_\_](#omega_vision.runtime.replay.AtomSpaceSemanticBackend.__init__)
    * [write\_once](#omega_vision.runtime.replay.AtomSpaceSemanticBackend.write_once)
    * [get](#omega_vision.runtime.replay.AtomSpaceSemanticBackend.get)
    * [values](#omega_vision.runtime.replay.AtomSpaceSemanticBackend.values)
  * [ActionTreeSemanticReplay](#omega_vision.runtime.replay.ActionTreeSemanticReplay)
    * [ORDER](#omega_vision.runtime.replay.ActionTreeSemanticReplay.ORDER)
    * [replay](#omega_vision.runtime.replay.ActionTreeSemanticReplay.replay)
* [omega\_vision.runtime.transcript](#omega_vision.runtime.transcript)
  * [TranscriptComparison](#omega_vision.runtime.transcript.TranscriptComparison)
    * [expected\_events](#omega_vision.runtime.transcript.TranscriptComparison.expected_events)
    * [actual\_events](#omega_vision.runtime.transcript.TranscriptComparison.actual_events)
    * [exact\_matches](#omega_vision.runtime.transcript.TranscriptComparison.exact_matches)
    * [ordered\_prefix\_matches](#omega_vision.runtime.transcript.TranscriptComparison.ordered_prefix_matches)
    * [event\_recall](#omega_vision.runtime.transcript.TranscriptComparison.event_recall)
    * [exact](#omega_vision.runtime.transcript.TranscriptComparison.exact)
  * [TranscriptScorer](#omega_vision.runtime.transcript.TranscriptScorer)
    * [compare](#omega_vision.runtime.transcript.TranscriptScorer.compare)

<a id="omega_vision.adapters.adapters"></a>

# omega\_vision.adapters.adapters

<a id="omega_vision.adapters.adapters.LearnedPartRoleProvider"></a>

## LearnedPartRoleProvider Objects

```python
class LearnedPartRoleProvider()
```

Infer semantic component roles from labeled structural examples.

The provider deliberately learns only the label boundary. Component
extraction and role-reference validation remain deterministic adapter
responsibilities.

<a id="omega_vision.adapters.adapters.LearnedPartRoleProvider.__init__"></a>

#### \_\_init\_\_

```python
def __init__(examples: Iterable[Mapping[str, Any]]) -> None
```

<a id="omega_vision.adapters.adapters.LearnedPartRoleProvider.infer_part_roles"></a>

#### infer\_part\_roles

```python
def infer_part_roles(
    _item: Mapping[str, Any], components: tuple[tuple[tuple[int, int], ...],
                                                ...]
) -> tuple[Mapping[str, Any], ...]
```

<a id="omega_vision.adapters.adapters.normalize_grid_structure"></a>

#### normalize\_grid\_structure

```python
def normalize_grid_structure(
        item: Mapping[str, Any],
        role_provider: Any | None = None) -> Mapping[str, Any]
```

Normalize extractor-specific grid structure into one semantic contract.

<a id="omega_vision.adapters.adapters.normalize_image_structure"></a>

#### normalize\_image\_structure

```python
def normalize_image_structure(
        item: Mapping[str, Any],
        role_provider: Any | None = None) -> Mapping[str, Any]
```

Preserve provider raster semantics in the shared normalized contract.

<a id="omega_vision.adapters.adapters.GridPerceptionBatch"></a>

## GridPerceptionBatch Objects

```python
@dataclass(frozen=True)
class GridPerceptionBatch()
```

<a id="omega_vision.adapters.adapters.GridPerceptionBatch.observation"></a>

#### observation: `Observation`

<a id="omega_vision.adapters.adapters.GridPerceptionBatch.candidates"></a>

#### candidates: `tuple[CandidateObject, ...]`

<a id="omega_vision.adapters.adapters.GridPerceptionBatch.extractor_details"></a>

#### extractor\_details: `Mapping[str, Mapping[str, Any]]`

<a id="omega_vision.adapters.adapters.MediaPerceptionBatch"></a>

## MediaPerceptionBatch Objects

```python
@dataclass(frozen=True)
class MediaPerceptionBatch()
```

<a id="omega_vision.adapters.adapters.MediaPerceptionBatch.observation"></a>

#### observation: `Observation`

<a id="omega_vision.adapters.adapters.MediaPerceptionBatch.candidates"></a>

#### candidates: `tuple[CandidateObject, ...]`

<a id="omega_vision.adapters.adapters.MediaPerceptionBatch.extractor_details"></a>

#### extractor\_details: `Mapping[str, Mapping[str, Any]]`

<a id="omega_vision.adapters.adapters.PerceptionAdapter"></a>

## PerceptionAdapter Objects

```python
class PerceptionAdapter(ABC)
```

Domain seam; core code must not import ARC or raster assumptions.

<a id="omega_vision.adapters.adapters.PerceptionAdapter.propose_candidates"></a>

#### propose\_candidates

```python
@abstractmethod
def propose_candidates(observation: Any) -> Iterable[CandidateObject]
```

<a id="omega_vision.adapters.adapters.GridAdapter"></a>

## GridAdapter Objects

```python
class GridAdapter(PerceptionAdapter)
```

Thin adapter around an existing grid object extractor.

<a id="omega_vision.adapters.adapters.GridAdapter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(extractor: Any,
             provider: Any,
             role_provider: Any | None = None) -> None
```

<a id="omega_vision.adapters.adapters.GridAdapter.normalize"></a>

#### normalize

```python
def normalize(*, observation_id: str, grid: Any, action_tree_node: str,
              artifact_uri: str) -> GridPerceptionBatch
```

Wrap the established extractor result in Phase 2 contracts.

<a id="omega_vision.adapters.adapters.GridAdapter.candidate_detail"></a>

#### candidate\_detail

```python
def candidate_detail(candidate_id: str) -> Mapping[str, Any]
```

<a id="omega_vision.adapters.adapters.GridAdapter.propose_candidates"></a>

#### propose\_candidates

```python
def propose_candidates(observation: Any) -> Iterable[CandidateObject]
```

<a id="omega_vision.adapters.adapters.ImageAdapter"></a>

## ImageAdapter Objects

```python
class ImageAdapter(PerceptionAdapter)
```

Normalize raster extractor output without prescribing segmentation.

<a id="omega_vision.adapters.adapters.ImageAdapter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(extractor: Any,
             provider: Any,
             role_provider: Any | None = None) -> None
```

<a id="omega_vision.adapters.adapters.ImageAdapter.normalize"></a>

#### normalize

```python
def normalize(*,
              observation_id: str,
              image: Any,
              action_tree_node: str,
              artifact_uri: str,
              sequence: int | None = None) -> MediaPerceptionBatch
```

<a id="omega_vision.adapters.adapters.ImageAdapter.candidate_detail"></a>

#### candidate\_detail

```python
def candidate_detail(candidate_id: str) -> Mapping[str, Any]
```

<a id="omega_vision.adapters.adapters.ImageAdapter.propose_candidates"></a>

#### propose\_candidates

```python
def propose_candidates(observation: Any) -> Iterable[CandidateObject]
```

<a id="omega_vision.adapters.adapters.SimpleVideoAdapter"></a>

## SimpleVideoAdapter Objects

```python
class SimpleVideoAdapter(PerceptionAdapter)
```

Adapt an ordered iterable of decoded frames through an ImageAdapter.

<a id="omega_vision.adapters.adapters.SimpleVideoAdapter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(image_adapter: ImageAdapter) -> None
```

<a id="omega_vision.adapters.adapters.SimpleVideoAdapter.normalize"></a>

#### normalize

```python
def normalize(*, observation_id: str, frames: Iterable[Any],
              action_tree_node: str,
              artifact_uri: str) -> tuple[MediaPerceptionBatch, ...]
```

<a id="omega_vision.adapters.adapters.SimpleVideoAdapter.propose_candidates"></a>

#### propose\_candidates

```python
def propose_candidates(observation: Any) -> Iterable[CandidateObject]
```

<a id="omega_vision.adapters.providers"></a>

# omega\_vision.adapters.providers

<a id="omega_vision.adapters.providers.ProviderCapabilities"></a>

## ProviderCapabilities Objects

```python
@dataclass(frozen=True)
class ProviderCapabilities()
```

<a id="omega_vision.adapters.providers.ProviderCapabilities.mode"></a>

#### mode: `ExecutionMode`

<a id="omega_vision.adapters.providers.ProviderCapabilities.candidate_parts"></a>

#### candidate\_parts: `tuple[str, ...]`

<a id="omega_vision.adapters.providers.ProviderCapabilities.semantic_record_families"></a>

#### semantic\_record\_families: `tuple[str, ...]`

<a id="omega_vision.adapters.providers.ProviderCapabilities.dynamic_candidate_parts"></a>

#### dynamic\_candidate\_parts: `bool`

<a id="omega_vision.adapters.providers.ProviderCapabilities.supports_candidate_part"></a>

#### supports\_candidate\_part

```python
def supports_candidate_part(name: str) -> bool
```

<a id="omega_vision.adapters.providers.UnsupportedProviderCapability"></a>

## UnsupportedProviderCapability Objects

```python
class UnsupportedProviderCapability(KeyError)
```

Machine-readable failure for a capability the provider does not expose.

<a id="omega_vision.adapters.providers.UnsupportedProviderCapability.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*, mode: ExecutionMode, capability_kind: str, requested: str,
             available: tuple[str, ...]) -> None
```

<a id="omega_vision.adapters.providers.UnsupportedProviderCapability.as_dict"></a>

#### as\_dict

```python
def as_dict() -> dict[str, Any]
```

<a id="omega_vision.adapters.providers.ArtifactProvider"></a>

## ArtifactProvider Objects

```python
class ArtifactProvider(ABC)
```

One stable contract with backend-specific implementations.

<a id="omega_vision.adapters.providers.ArtifactProvider.mode"></a>

#### mode: `ExecutionMode`

<a id="omega_vision.adapters.providers.ArtifactProvider.capabilities"></a>

#### capabilities

```python
@abstractmethod
def capabilities() -> ProviderCapabilities
```

<a id="omega_vision.adapters.providers.ArtifactProvider.get_candidate_part"></a>

#### get\_candidate\_part

```python
@abstractmethod
def get_candidate_part(candidate: CandidateObject,
                       name: str) -> NormalizedResult
```

<a id="omega_vision.adapters.providers.PythonProvider"></a>

## PythonProvider Objects

```python
class PythonProvider(ArtifactProvider)
```

<a id="omega_vision.adapters.providers.PythonProvider.mode"></a>

#### mode

<a id="omega_vision.adapters.providers.PythonProvider.__init__"></a>

#### \_\_init\_\_

```python
def __init__(
        resolvers: Mapping[str, Callable[[CandidateObject], Any]]) -> None
```

<a id="omega_vision.adapters.providers.PythonProvider.capabilities"></a>

#### capabilities

```python
def capabilities() -> ProviderCapabilities
```

<a id="omega_vision.adapters.providers.PythonProvider.get_candidate_part"></a>

#### get\_candidate\_part

```python
def get_candidate_part(candidate: CandidateObject,
                       name: str) -> NormalizedResult
```

<a id="omega_vision.adapters.providers.GptArtifactProvider"></a>

## GptArtifactProvider Objects

```python
class GptArtifactProvider(ArtifactProvider)
```

Reads GPT-generated or cached artifacts; it does not emulate native analysis.

<a id="omega_vision.adapters.providers.GptArtifactProvider.mode"></a>

#### mode

<a id="omega_vision.adapters.providers.GptArtifactProvider.ARTIFACT_NAMES"></a>

#### ARTIFACT\_NAMES

<a id="omega_vision.adapters.providers.GptArtifactProvider.__init__"></a>

#### \_\_init\_\_

```python
def __init__(node_path: str | Path) -> None
```

<a id="omega_vision.adapters.providers.GptArtifactProvider.capabilities"></a>

#### capabilities

```python
def capabilities() -> ProviderCapabilities
```

<a id="omega_vision.adapters.providers.GptArtifactProvider.get_candidate_part"></a>

#### get\_candidate\_part

```python
def get_candidate_part(candidate: CandidateObject,
                       name: str) -> NormalizedResult
```

<a id="omega_vision.adapters.providers.PrologProvider"></a>

## PrologProvider Objects

```python
class PrologProvider(ArtifactProvider)
```

Delegates symbolic queries to SWI-Prolog through an injected query function.

<a id="omega_vision.adapters.providers.PrologProvider.mode"></a>

#### mode

<a id="omega_vision.adapters.providers.PrologProvider.SEMANTIC_NAMESPACES"></a>

#### SEMANTIC\_NAMESPACES

<a id="omega_vision.adapters.providers.PrologProvider.__init__"></a>

#### \_\_init\_\_

```python
def __init__(query: Callable[[str, Mapping[str, Any]], Any]) -> None
```

<a id="omega_vision.adapters.providers.PrologProvider.capabilities"></a>

#### capabilities

```python
def capabilities() -> ProviderCapabilities
```

<a id="omega_vision.adapters.providers.PrologProvider.get_candidate_part"></a>

#### get\_candidate\_part

```python
def get_candidate_part(candidate: CandidateObject,
                       name: str) -> NormalizedResult
```

<a id="omega_vision.adapters.providers.PrologProvider.get_semantic_records"></a>

#### get\_semantic\_records

```python
def get_semantic_records(
        name: str,
        filters: Mapping[str, Any] | None = None) -> NormalizedResult
```

Query one normalized semantic namespace through the Prolog adapter.

<a id="omega_vision.adapters.sprite"></a>

# omega\_vision.adapters.sprite

<a id="omega_vision.adapters.sprite.AlphaContourProvider"></a>

## AlphaContourProvider Objects

```python
class AlphaContourProvider()
```

Extract transparent sprites and exact pixel-boundary vector contours.

<a id="omega_vision.adapters.sprite.AlphaContourProvider.__call__"></a>

#### \_\_call\_\_

```python
def __call__(image: Image.Image) -> Mapping[str, Any]
```

<a id="omega_vision.adapters.sprite.SpriteAdapter"></a>

## SpriteAdapter Objects

```python
class SpriteAdapter(ImageAdapter)
```

Image adapter preconfigured for transparent sprite sheets.

<a id="omega_vision.adapters.sprite.SpriteAdapter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(provider: Any, extractor: Any | None = None) -> None
```

<a id="omega_vision.core.learning"></a>

# omega\_vision.core.learning

<a id="omega_vision.core.learning.TransitionRecord"></a>

## TransitionRecord Objects

```python
@dataclass(frozen=True)
class TransitionRecord()
```

<a id="omega_vision.core.learning.TransitionRecord.before_state_id"></a>

#### before\_state\_id: `str`

<a id="omega_vision.core.learning.TransitionRecord.action_or_event"></a>

#### action\_or\_event: `Any`

<a id="omega_vision.core.learning.TransitionRecord.after_state_id"></a>

#### after\_state\_id: `str`

<a id="omega_vision.core.learning.TransitionRecord.changes"></a>

#### changes: `tuple[Any, ...]`

<a id="omega_vision.core.learning.TransitionRecord.provenance"></a>

#### provenance: `tuple[str, ...]`

<a id="omega_vision.core.learning.TransformationCandidate"></a>

## TransformationCandidate Objects

```python
@dataclass(frozen=True)
class TransformationCandidate()
```

<a id="omega_vision.core.learning.TransformationCandidate.candidate_id"></a>

#### candidate\_id: `str`

<a id="omega_vision.core.learning.TransformationCandidate.transformation"></a>

#### transformation: `Any`

<a id="omega_vision.core.learning.TransformationCandidate.evidence"></a>

#### evidence: `tuple[Any, ...]`

<a id="omega_vision.core.learning.TransformationCandidate.score"></a>

#### score: `float`

<a id="omega_vision.core.learning.TransformationCandidate.source_state_id"></a>

#### source\_state\_id: `str | None`

<a id="omega_vision.core.learning.TransformationCandidate.target_state_id"></a>

#### target\_state\_id: `str | None`

<a id="omega_vision.core.learning.TransformationCandidate.action_or_event"></a>

#### action\_or\_event: `Any`

<a id="omega_vision.core.learning.TransformationCandidate.assumptions"></a>

#### assumptions: `tuple[str, ...]`

<a id="omega_vision.core.learning.TransformationCandidate.critiques"></a>

#### critiques: `tuple[str, ...]`

<a id="omega_vision.core.learning.TransformationCandidate.provenance"></a>

#### provenance: `tuple[str, ...]`

<a id="omega_vision.core.learning.RuleEvidence"></a>

## RuleEvidence Objects

```python
@dataclass(frozen=True)
class RuleEvidence()
```

<a id="omega_vision.core.learning.RuleEvidence.rule_id"></a>

#### rule\_id: `str`

<a id="omega_vision.core.learning.RuleEvidence.confirming"></a>

#### confirming: `tuple[Any, ...]`

<a id="omega_vision.core.learning.RuleEvidence.refuting"></a>

#### refuting: `tuple[Any, ...]`

<a id="omega_vision.core.learning.RuleRivalSet"></a>

## RuleRivalSet Objects

```python
@dataclass(frozen=True)
class RuleRivalSet()
```

<a id="omega_vision.core.learning.RuleRivalSet.rules"></a>

#### rules: `tuple[TransitionRule, ...]`

<a id="omega_vision.core.learning.PredictionGradeStatus"></a>

## PredictionGradeStatus Objects

```python
class PredictionGradeStatus(str, Enum)
```

<a id="omega_vision.core.learning.PredictionGradeStatus.SUCCESS"></a>

#### SUCCESS

<a id="omega_vision.core.learning.PredictionGradeStatus.FAILURE"></a>

#### FAILURE

<a id="omega_vision.core.learning.PredictionGradeStatus.PARTIAL_MATCH"></a>

#### PARTIAL\_MATCH

<a id="omega_vision.core.learning.PredictionGradeStatus.CONTRADICTION"></a>

#### CONTRADICTION

<a id="omega_vision.core.learning.PredictionGradeStatus.UNGRADABLE"></a>

#### UNGRADABLE

<a id="omega_vision.core.learning.PredictionGrade"></a>

## PredictionGrade Objects

```python
@dataclass(frozen=True)
class PredictionGrade()
```

<a id="omega_vision.core.learning.PredictionGrade.score"></a>

#### score: `float | None`

<a id="omega_vision.core.learning.PredictionGrade.evidence"></a>

#### evidence: `tuple[Any, ...]`

<a id="omega_vision.core.learning.PredictionGrade.status"></a>

#### status: `PredictionGradeStatus | None`

<a id="omega_vision.core.learning.PredictionGrade.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="omega_vision.core.learning.TransitionAnalyzer"></a>

## TransitionAnalyzer Objects

```python
class TransitionAnalyzer()
```

Facade over a deterministic, Prolog, or GPT-backed transition analyzer.

<a id="omega_vision.core.learning.TransitionAnalyzer.__init__"></a>

#### \_\_init\_\_

```python
def __init__(analyze: Callable[[Any, Any, Any], TransitionRecord]) -> None
```

<a id="omega_vision.core.learning.TransitionAnalyzer.analyze"></a>

#### analyze

```python
def analyze(before: Any, action_or_event: Any, after: Any) -> TransitionRecord
```

<a id="omega_vision.core.learning.TransformationLearner"></a>

## TransformationLearner Objects

```python
class TransformationLearner()
```

Delegates candidate generation without fixing the learning algorithm.

<a id="omega_vision.core.learning.TransformationLearner.__init__"></a>

#### \_\_init\_\_

```python
def __init__(
    learn: Callable[[TransitionRecord], Iterable[TransformationCandidate]]
) -> None
```

<a id="omega_vision.core.learning.TransformationLearner.learn"></a>

#### learn

```python
def learn(transition: TransitionRecord) -> tuple[TransformationCandidate, ...]
```

<a id="omega_vision.core.learning.RuleInducer"></a>

## RuleInducer Objects

```python
class RuleInducer()
```

Converts transformation candidates into normalized TransitionRule records.

<a id="omega_vision.core.learning.RuleInducer.__init__"></a>

#### \_\_init\_\_

```python
def __init__(
    induce: Callable[[Sequence[TransformationCandidate]],
                     Iterable[TransitionRule]]
) -> None
```

<a id="omega_vision.core.learning.RuleInducer.induce"></a>

#### induce

```python
def induce(
    candidates: Sequence[TransformationCandidate]
) -> tuple[TransitionRule, ...]
```

<a id="omega_vision.core.learning.RuleRanker"></a>

## RuleRanker Objects

```python
class RuleRanker()
```

<a id="omega_vision.core.learning.RuleRanker.__init__"></a>

#### \_\_init\_\_

```python
def __init__(score: Callable[[TransitionRule], float]) -> None
```

<a id="omega_vision.core.learning.RuleRanker.rank"></a>

#### rank

```python
def rank(rules: Iterable[TransitionRule]) -> tuple[TransitionRule, ...]
```

<a id="omega_vision.core.learning.RuleExecutor"></a>

## RuleExecutor Objects

```python
class RuleExecutor()
```

Applies stored rules through caller-supplied domain semantics.

<a id="omega_vision.core.learning.RuleExecutor.__init__"></a>

#### \_\_init\_\_

```python
def __init__(store: RuleStore, checker: Callable[[TransitionRule, Any], bool],
             executor: Callable[[TransitionRule, Any], Any]) -> None
```

<a id="omega_vision.core.learning.RuleExecutor.applicable"></a>

#### applicable

```python
def applicable(rule_id: str, state: Any) -> bool
```

<a id="omega_vision.core.learning.RuleExecutor.apply"></a>

#### apply

```python
def apply(rule_id: str, state: Any) -> Any
```

<a id="omega_vision.core.learning.OutcomeChannel"></a>

## OutcomeChannel Objects

```python
class OutcomeChannel()
```

Independent observation channel used to grade a prior prediction.

<a id="omega_vision.core.learning.OutcomeChannel.__init__"></a>

#### \_\_init\_\_

```python
def __init__(read: Callable[[], Any]) -> None
```

<a id="omega_vision.core.learning.OutcomeChannel.read"></a>

#### read

```python
def read() -> Any
```

<a id="omega_vision.core.learning.PredictionEvaluator"></a>

## PredictionEvaluator Objects

```python
class PredictionEvaluator()
```

<a id="omega_vision.core.learning.PredictionEvaluator.__init__"></a>

#### \_\_init\_\_

```python
def __init__(compare: Callable[[Any, Any], PredictionGrade]) -> None
```

<a id="omega_vision.core.learning.PredictionEvaluator.evaluate"></a>

#### evaluate

```python
def evaluate(predicted: Any, observed: Any) -> PredictionGrade
```

<a id="omega_vision.core.learning.LearningStepResult"></a>

## LearningStepResult Objects

```python
@dataclass(frozen=True)
class LearningStepResult()
```

<a id="omega_vision.core.learning.LearningStepResult.transition"></a>

#### transition: `TransitionRecord`

<a id="omega_vision.core.learning.LearningStepResult.candidates"></a>

#### candidates: `tuple[TransformationCandidate, ...]`

<a id="omega_vision.core.learning.LearningStepResult.rules"></a>

#### rules: `tuple[TransitionRule, ...]`

<a id="omega_vision.core.learning.GameLearningPipeline"></a>

## GameLearningPipeline Objects

```python
class GameLearningPipeline()
```

Connected Phase 3 flow; algorithms remain replaceable providers.

<a id="omega_vision.core.learning.GameLearningPipeline.__init__"></a>

#### \_\_init\_\_

```python
def __init__(transition_analyzer: TransitionAnalyzer,
             transformation_learner: TransformationLearner,
             rule_inducer: RuleInducer,
             rule_ranker: RuleRanker,
             rule_store: RuleStore,
             prediction_ledger: PredictionLedger,
             semantic_store: Any | None = None) -> None
```

<a id="omega_vision.core.learning.GameLearningPipeline.learn_transition"></a>

#### learn\_transition

```python
def learn_transition(before: Any, action_or_event: Any,
                     after: Any) -> LearningStepResult
```

<a id="omega_vision.core.learning.GameLearningPipeline.recommend_action"></a>

#### recommend\_action

```python
def recommend_action(
        *,
        source_state_id: str,
        attempted_action: Any,
        created_sequence: int,
        prediction_id: str | None = None) -> ActionRecommendation | None
```

Rank all learned actions independently of the action being attempted.

<a id="omega_vision.core.learning.GameLearningPipeline.predict"></a>

#### predict

```python
def predict(*, prediction_id: str, rule_id: str, source_state_id: str,
            state: Any, created_sequence: int,
            executor: RuleExecutor) -> tuple[Any, PredictionRecord]
```

<a id="omega_vision.core.learning.GameLearningPipeline.grade_prediction"></a>

#### grade\_prediction

```python
def grade_prediction(*, prediction_id: str, outcome_sequence: int,
                     outcome_channel: OutcomeChannel,
                     evaluator: PredictionEvaluator) -> PredictionRecord
```

<a id="omega_vision.core.memory"></a>

# omega\_vision.core.memory

<a id="omega_vision.core.memory.EncounterLog"></a>

## EncounterLog Objects

```python
class EncounterLog()
```

Append-only semantic encounters with deterministic, idempotent replay.

Phase 1 remains the owner of action-tree history. This log only records the
Phase 2 semantic encounters linked to those immutable node references.

<a id="omega_vision.core.memory.EncounterLog.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

<a id="omega_vision.core.memory.EncounterLog.append"></a>

#### append

```python
def append(encounter: EncounterRecord) -> EncounterRecord
```

<a id="omega_vision.core.memory.EncounterLog.get"></a>

#### get

```python
def get(encounter_id: str) -> EncounterRecord | None
```

<a id="omega_vision.core.memory.EncounterLog.records"></a>

#### records

```python
def records() -> tuple[EncounterRecord, ...]
```

<a id="omega_vision.core.memory.EncounterLog.for_object"></a>

#### for\_object

```python
def for_object(object_identity_id: str) -> tuple[EncounterRecord, ...]
```

<a id="omega_vision.core.memory.EncounterLog.replay"></a>

#### replay

```python
def replay(encounters: tuple[EncounterRecord, ...]) -> "EncounterLog"
```

<a id="omega_vision.core.memory.EncounterLog.deterministic_hash"></a>

#### deterministic\_hash

```python
def deterministic_hash() -> str
```

<a id="omega_vision.core.memory.ResidualGate"></a>

## ResidualGate Objects

```python
class ResidualGate()
```

Deterministic admission policy; thresholds remain configuration choices.

<a id="omega_vision.core.memory.ResidualGate.evaluate"></a>

#### evaluate

```python
def evaluate(residual: ResidualCandidate) -> ResidualDisposition
```

<a id="omega_vision.core.memory.SymbolicMemory"></a>

## SymbolicMemory Objects

```python
class SymbolicMemory()
```

Small in-memory reference store; durable stores may implement this API.

<a id="omega_vision.core.memory.SymbolicMemory.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

<a id="omega_vision.core.memory.SymbolicMemory.get"></a>

#### get

```python
def get(handle: str) -> CommittedAtom | None
```

<a id="omega_vision.core.memory.SymbolicMemory.all_atoms"></a>

#### all\_atoms

```python
def all_atoms() -> tuple[CommittedAtom, ...]
```

<a id="omega_vision.core.memory.SymbolicMemory.events"></a>

#### events

```python
def events() -> tuple[dict[str, Any], ...]
```

<a id="omega_vision.core.memory.SymbolicMemory.evidence_for"></a>

#### evidence\_for

```python
def evidence_for(handle: str) -> tuple[EvidenceRecord, ...]
```

<a id="omega_vision.core.memory.SymbolicMemory.identity_decision"></a>

#### identity\_decision

```python
def identity_decision(
        decision_id: str) -> MergeDecision | SplitDecision | None
```

<a id="omega_vision.core.memory.SymbolicMemory.confidence_history"></a>

#### confidence\_history

```python
def confidence_history(handle: str) -> tuple[ConfidenceHistoryRecord, ...]
```

<a id="omega_vision.core.memory.SymbolicMemory.checkpoints"></a>

#### checkpoints

```python
def checkpoints() -> tuple[IdentityMemoryCheckpoint, ...]
```

<a id="omega_vision.core.memory.SymbolicMemory.restore"></a>

#### restore

```python
def restore(checkpoint: IdentityMemoryCheckpoint) -> "SymbolicMemory"
```

Restore an exact writer state from one durable checkpoint.

<a id="omega_vision.core.memory.SingleWriter"></a>

## SingleWriter Objects

```python
class SingleWriter()
```

Only mutation path for committed atoms and their evidence.

<a id="omega_vision.core.memory.SingleWriter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(
    memory: SymbolicMemory,
    checkpoint_sink: Callable[[IdentityMemoryCheckpoint], Any] | None = None
) -> None
```

<a id="omega_vision.core.memory.SingleWriter.commit"></a>

#### commit

```python
def commit(atom: CommittedAtom) -> CommittedAtom
```

<a id="omega_vision.core.memory.SingleWriter.commit_residual"></a>

#### commit\_residual

```python
def commit_residual(residual: ResidualCandidate, atom: CommittedAtom,
                    gate: ResidualGate) -> CommittedAtom
```

Commit only a residual that the configured gate admits.

<a id="omega_vision.core.memory.SingleWriter.accrue_evidence"></a>

#### accrue\_evidence

```python
def accrue_evidence(handle: str, confidence: float,
                    evidence: str) -> CommittedAtom
```

Compatibility path for legacy callers with pre-calibrated evidence.

<a id="omega_vision.core.memory.SingleWriter.apply_evidence"></a>

#### apply\_evidence

```python
def apply_evidence(handle: str, evidence: EvidenceRecord) -> CommittedAtom
```

Derive calibrated confidence from attributable signed evidence.

<a id="omega_vision.core.memory.SingleWriter.tombstone"></a>

#### tombstone

```python
def tombstone(handle: str, reason: str) -> CommittedAtom
```

<a id="omega_vision.core.memory.SingleWriter.demote"></a>

#### demote

```python
def demote(handle: str,
           reason: str,
           *,
           checkpoint: bool = True) -> CommittedAtom
```

<a id="omega_vision.core.memory.SingleWriter.merge_identities"></a>

#### merge\_identities

```python
def merge_identities(decision: MergeDecision,
                     resulting_atom: CommittedAtom) -> CommittedAtom
```

<a id="omega_vision.core.memory.SingleWriter.split_identity"></a>

#### split\_identity

```python
def split_identity(
        decision: SplitDecision,
        resulting_atoms: tuple[CommittedAtom,
                               ...]) -> tuple[CommittedAtom, ...]
```

<a id="omega_vision.core.memory.SingleWriter.reverse_identity_decision"></a>

#### reverse\_identity\_decision

```python
def reverse_identity_decision(decision_id: str, reason: str) -> None
```

<a id="omega_vision.core.models"></a>

# omega\_vision.core.models

<a id="omega_vision.core.models.PHASE2_SCHEMA_VERSION"></a>

#### PHASE2\_SCHEMA\_VERSION

<a id="omega_vision.core.models.deterministic_identifier"></a>

#### deterministic\_identifier

```python
def deterministic_identifier(record_type: str, identity: Mapping[str,
                                                                 Any]) -> str
```

Create a reproducible identifier from the record's immutable identity.

<a id="omega_vision.core.models.ExecutionMode"></a>

## ExecutionMode Objects

```python
class ExecutionMode(str, Enum)
```

<a id="omega_vision.core.models.ExecutionMode.PROLOG"></a>

#### PROLOG

<a id="omega_vision.core.models.ExecutionMode.GPT"></a>

#### GPT

<a id="omega_vision.core.models.ExecutionMode.PYTHON"></a>

#### PYTHON

<a id="omega_vision.core.models.ResidualDisposition"></a>

## ResidualDisposition Objects

```python
class ResidualDisposition(str, Enum)
```

<a id="omega_vision.core.models.ResidualDisposition.ABSORBED"></a>

#### ABSORBED

<a id="omega_vision.core.models.ResidualDisposition.PROVISIONAL"></a>

#### PROVISIONAL

<a id="omega_vision.core.models.ResidualDisposition.COMMIT_REQUEST"></a>

#### COMMIT\_REQUEST

<a id="omega_vision.core.models.EvidencePolarity"></a>

## EvidencePolarity Objects

```python
class EvidencePolarity(str, Enum)
```

<a id="omega_vision.core.models.EvidencePolarity.SUPPORTS"></a>

#### SUPPORTS

<a id="omega_vision.core.models.EvidencePolarity.CONTRADICTS"></a>

#### CONTRADICTS

<a id="omega_vision.core.models.IdentityDecision"></a>

## IdentityDecision Objects

```python
class IdentityDecision(str, Enum)
```

<a id="omega_vision.core.models.IdentityDecision.PROPOSED"></a>

#### PROPOSED

<a id="omega_vision.core.models.IdentityDecision.ACCEPTED"></a>

#### ACCEPTED

<a id="omega_vision.core.models.IdentityDecision.REJECTED"></a>

#### REJECTED

<a id="omega_vision.core.models.IdentityDecision.REVERSED"></a>

#### REVERSED

<a id="omega_vision.core.models.ProvenanceRef"></a>

## ProvenanceRef Objects

```python
@dataclass(frozen=True)
class ProvenanceRef()
```

<a id="omega_vision.core.models.ProvenanceRef.source_id"></a>

#### source\_id: `str`

<a id="omega_vision.core.models.ProvenanceRef.provider"></a>

#### provider: `str`

<a id="omega_vision.core.models.ProvenanceRef.action_tree_node"></a>

#### action\_tree\_node: `str | None`

<a id="omega_vision.core.models.ProvenanceRef.artifact_id"></a>

#### artifact\_id: `str | None`

<a id="omega_vision.core.models.ProvenanceRef.sequence"></a>

#### sequence: `int | None`

<a id="omega_vision.core.models.ProvenanceRef.metadata"></a>

#### metadata: `Mapping[str, Any]`

<a id="omega_vision.core.models.ProvenanceRef.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.ProvenanceRef.create"></a>

#### create

```python
@classmethod
def create(cls, *, source_id: str, provider: str,
           **values: Any) -> "ProvenanceRef"
```

<a id="omega_vision.core.models.ArtifactRef"></a>

## ArtifactRef Objects

```python
@dataclass(frozen=True)
class ArtifactRef()
```

<a id="omega_vision.core.models.ArtifactRef.artifact_id"></a>

#### artifact\_id: `str`

<a id="omega_vision.core.models.ArtifactRef.artifact_type"></a>

#### artifact\_type: `str`

<a id="omega_vision.core.models.ArtifactRef.uri"></a>

#### uri: `str`

<a id="omega_vision.core.models.ArtifactRef.content_hash"></a>

#### content\_hash: `str | None`

<a id="omega_vision.core.models.ArtifactRef.media_type"></a>

#### media\_type: `str | None`

<a id="omega_vision.core.models.ArtifactRef.provenance"></a>

#### provenance: `tuple[ProvenanceRef, ...]`

<a id="omega_vision.core.models.ArtifactRef.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.ArtifactRef.create"></a>

#### create

```python
@classmethod
def create(cls,
           *,
           artifact_type: str,
           uri: str,
           content_hash: str | None = None,
           **values: Any) -> "ArtifactRef"
```

<a id="omega_vision.core.models.TurtleProgramRef"></a>

## TurtleProgramRef Objects

```python
@dataclass(frozen=True)
class TurtleProgramRef()
```

<a id="omega_vision.core.models.TurtleProgramRef.artifact"></a>

#### artifact: `ArtifactRef`

<a id="omega_vision.core.models.TurtleProgramRef.language"></a>

#### language: `str`

<a id="omega_vision.core.models.TurtleProgramRef.entrypoint"></a>

#### entrypoint: `str | None`

<a id="omega_vision.core.models.TurtleProgramRef.fit_score"></a>

#### fit\_score: `float | None`

<a id="omega_vision.core.models.TurtleProgramRef.distance"></a>

#### distance: `float | None`

<a id="omega_vision.core.models.TurtleProgramRef.residual_score"></a>

#### residual\_score: `float | None`

<a id="omega_vision.core.models.TurtleProgramRef.description_length"></a>

#### description\_length: `float | None`

<a id="omega_vision.core.models.TurtleProgramRef.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.InstanceParameters"></a>

## InstanceParameters Objects

```python
@dataclass(frozen=True)
class InstanceParameters()
```

<a id="omega_vision.core.models.InstanceParameters.position"></a>

#### position: `tuple[float, ...]`

<a id="omega_vision.core.models.InstanceParameters.orientation"></a>

#### orientation: `float | str | None`

<a id="omega_vision.core.models.InstanceParameters.scale"></a>

#### scale: `tuple[float, ...]`

<a id="omega_vision.core.models.InstanceParameters.appearance"></a>

#### appearance: `Mapping[str, Any]`

<a id="omega_vision.core.models.InstanceParameters.supported_transformations"></a>

#### supported\_transformations: `tuple[str, ...]`

<a id="omega_vision.core.models.InstanceParameters.reflection"></a>

#### reflection: `str | None`

<a id="omega_vision.core.models.InstanceParameters.visibility"></a>

#### visibility: `float`

<a id="omega_vision.core.models.InstanceParameters.noise_score"></a>

#### noise\_score: `float`

<a id="omega_vision.core.models.InstanceParameters.geometry"></a>

#### geometry: `Mapping[str, Any]`

<a id="omega_vision.core.models.InstanceParameters.topology"></a>

#### topology: `Mapping[str, Any]`

<a id="omega_vision.core.models.InstanceParameters.relationships"></a>

#### relationships: `tuple[Mapping[str, Any], ...]`

<a id="omega_vision.core.models.InstanceParameters.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.EvidenceRecord"></a>

## EvidenceRecord Objects

```python
@dataclass(frozen=True)
class EvidenceRecord()
```

<a id="omega_vision.core.models.EvidenceRecord.evidence_id"></a>

#### evidence\_id: `str`

<a id="omega_vision.core.models.EvidenceRecord.subject_id"></a>

#### subject\_id: `str`

<a id="omega_vision.core.models.EvidenceRecord.polarity"></a>

#### polarity: `EvidencePolarity`

<a id="omega_vision.core.models.EvidenceRecord.source"></a>

#### source: `ProvenanceRef`

<a id="omega_vision.core.models.EvidenceRecord.weight"></a>

#### weight: `float`

<a id="omega_vision.core.models.EvidenceRecord.detail"></a>

#### detail: `Mapping[str, Any]`

<a id="omega_vision.core.models.EvidenceRecord.created_sequence"></a>

#### created\_sequence: `int`

<a id="omega_vision.core.models.EvidenceRecord.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.EvidenceRecord.create"></a>

#### create

```python
@classmethod
def create(cls,
           *,
           subject_id: str,
           polarity: EvidencePolarity,
           source: ProvenanceRef,
           weight: float = 1.0,
           detail: Mapping[str, Any] | None = None,
           created_sequence: int = 0) -> "EvidenceRecord"
```

<a id="omega_vision.core.models.Observation"></a>

## Observation Objects

```python
@dataclass(frozen=True)
class Observation()
```

<a id="omega_vision.core.models.Observation.observation_id"></a>

#### observation\_id: `str`

<a id="omega_vision.core.models.Observation.source_modality"></a>

#### source\_modality: `str`

<a id="omega_vision.core.models.Observation.artifacts"></a>

#### artifacts: `tuple[ArtifactRef, ...]`

<a id="omega_vision.core.models.Observation.dimensions"></a>

#### dimensions: `tuple[int, ...]`

<a id="omega_vision.core.models.Observation.coordinate_contract"></a>

#### coordinate\_contract: `str`

<a id="omega_vision.core.models.Observation.candidate_object_ids"></a>

#### candidate\_object\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.Observation.action_tree_node"></a>

#### action\_tree\_node: `str | None`

<a id="omega_vision.core.models.Observation.provenance"></a>

#### provenance: `tuple[ProvenanceRef, ...]`

<a id="omega_vision.core.models.Observation.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.Observation.create"></a>

#### create

```python
@classmethod
def create(
    cls,
    *,
    source_modality: str,
    artifacts: tuple[ArtifactRef, ...] = (),
    dimensions: tuple[int, ...] = (),
    coordinate_contract: str = "",
    candidate_object_ids: tuple[str, ...] = (),
    action_tree_node: str | None = None,
    provenance: tuple[ProvenanceRef, ...] = ()
) -> "Observation"
```

<a id="omega_vision.core.models.MatchProposal"></a>

## MatchProposal Objects

```python
@dataclass(frozen=True)
class MatchProposal()
```

<a id="omega_vision.core.models.MatchProposal.proposal_id"></a>

#### proposal\_id: `str`

<a id="omega_vision.core.models.MatchProposal.candidate_id"></a>

#### candidate\_id: `str`

<a id="omega_vision.core.models.MatchProposal.stored_identity_id"></a>

#### stored\_identity\_id: `str`

<a id="omega_vision.core.models.MatchProposal.matched_properties"></a>

#### matched\_properties: `tuple[str, ...]`

<a id="omega_vision.core.models.MatchProposal.changed_properties"></a>

#### changed\_properties: `Mapping[str, Any]`

<a id="omega_vision.core.models.MatchProposal.allowed_transformations"></a>

#### allowed\_transformations: `tuple[str, ...]`

<a id="omega_vision.core.models.MatchProposal.similarity"></a>

#### similarity: `float | None`

<a id="omega_vision.core.models.MatchProposal.retrieval_score"></a>

#### retrieval\_score: `float | None`

<a id="omega_vision.core.models.MatchProposal.retrieval_source"></a>

#### retrieval\_source: `str | None`

<a id="omega_vision.core.models.MatchProposal.probability"></a>

#### probability: `float | None`

<a id="omega_vision.core.models.MatchProposal.probability_source"></a>

#### probability\_source: `str | None`

<a id="omega_vision.core.models.MatchProposal.evidence_ids"></a>

#### evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.MatchProposal.provenance"></a>

#### provenance: `tuple[ProvenanceRef, ...]`

<a id="omega_vision.core.models.MatchProposal.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.MatchProposal.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="omega_vision.core.models.MatchProposal.create"></a>

#### create

```python
@classmethod
def create(cls, *, candidate_id: str, stored_identity_id: str,
           **values: Any) -> "MatchProposal"
```

<a id="omega_vision.core.models.MergeDecision"></a>

## MergeDecision Objects

```python
@dataclass(frozen=True)
class MergeDecision()
```

<a id="omega_vision.core.models.MergeDecision.decision_id"></a>

#### decision\_id: `str`

<a id="omega_vision.core.models.MergeDecision.identity_ids"></a>

#### identity\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.MergeDecision.resulting_identity_id"></a>

#### resulting\_identity\_id: `str`

<a id="omega_vision.core.models.MergeDecision.status"></a>

#### status: `IdentityDecision`

<a id="omega_vision.core.models.MergeDecision.evidence_ids"></a>

#### evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.MergeDecision.provenance"></a>

#### provenance: `tuple[ProvenanceRef, ...]`

<a id="omega_vision.core.models.MergeDecision.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.MergeDecision.create"></a>

#### create

```python
@classmethod
def create(cls, *, identity_ids: tuple[str, ...], resulting_identity_id: str,
           status: IdentityDecision, **values: Any) -> "MergeDecision"
```

<a id="omega_vision.core.models.SplitDecision"></a>

## SplitDecision Objects

```python
@dataclass(frozen=True)
class SplitDecision()
```

<a id="omega_vision.core.models.SplitDecision.decision_id"></a>

#### decision\_id: `str`

<a id="omega_vision.core.models.SplitDecision.source_identity_id"></a>

#### source\_identity\_id: `str`

<a id="omega_vision.core.models.SplitDecision.resulting_identity_ids"></a>

#### resulting\_identity\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.SplitDecision.status"></a>

#### status: `IdentityDecision`

<a id="omega_vision.core.models.SplitDecision.evidence_ids"></a>

#### evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.SplitDecision.provenance"></a>

#### provenance: `tuple[ProvenanceRef, ...]`

<a id="omega_vision.core.models.SplitDecision.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.SplitDecision.create"></a>

#### create

```python
@classmethod
def create(cls, *, source_identity_id: str, resulting_identity_ids: tuple[str,
                                                                          ...],
           status: IdentityDecision, **values: Any) -> "SplitDecision"
```

<a id="omega_vision.core.models.IdentityMemoryCheckpoint"></a>

## IdentityMemoryCheckpoint Objects

```python
@dataclass(frozen=True)
class IdentityMemoryCheckpoint()
```

Append-only, self-contained identity-writer state for durable recovery.

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.checkpoint_id"></a>

#### checkpoint\_id: `str`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.sequence"></a>

#### sequence: `int`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.event"></a>

#### event: `str`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.reference_id"></a>

#### reference\_id: `str | None`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.parent_checkpoint_id"></a>

#### parent\_checkpoint\_id: `str | None`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.atoms"></a>

#### atoms: `tuple[CommittedAtom, ...]`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.evidence"></a>

#### evidence: `tuple[EvidenceRecord, ...]`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.merge_decisions"></a>

#### merge\_decisions: `tuple[MergeDecision, ...]`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.split_decisions"></a>

#### split\_decisions: `tuple[SplitDecision, ...]`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.decision_snapshots"></a>

#### decision\_snapshots: `Mapping[
        str, Mapping[str, CommittedAtom | None]
    ]`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.confidence_history"></a>

#### confidence\_history: `tuple[ConfidenceHistoryRecord, ...]`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.create"></a>

#### create

```python
@classmethod
def create(
    cls, *, sequence: int, event: str, reference_id: str | None,
    parent_checkpoint_id: str | None, atoms: tuple[CommittedAtom, ...],
    evidence: tuple[EvidenceRecord, ...], merge_decisions: tuple[MergeDecision,
                                                                 ...],
    split_decisions: tuple[SplitDecision, ...],
    decision_snapshots: Mapping[str, Mapping[str, CommittedAtom | None]],
    confidence_history: tuple[ConfidenceHistoryRecord, ...]
) -> "IdentityMemoryCheckpoint"
```

<a id="omega_vision.core.models.IdentityMemoryCheckpoint.as_compaction_root"></a>

#### as\_compaction\_root

```python
def as_compaction_root() -> "IdentityMemoryCheckpoint"
```

Create a standalone root retaining the exact current writer state.

<a id="omega_vision.core.models.RecognitionAccount"></a>

## RecognitionAccount Objects

```python
@dataclass(frozen=True)
class RecognitionAccount()
```

<a id="omega_vision.core.models.RecognitionAccount.account_id"></a>

#### account\_id: `str`

<a id="omega_vision.core.models.RecognitionAccount.candidate_id"></a>

#### candidate\_id: `str`

<a id="omega_vision.core.models.RecognitionAccount.stored_identity_id"></a>

#### stored\_identity\_id: `str | None`

<a id="omega_vision.core.models.RecognitionAccount.matched_properties"></a>

#### matched\_properties: `tuple[str, ...]`

<a id="omega_vision.core.models.RecognitionAccount.changed_properties"></a>

#### changed\_properties: `Mapping[str, Any]`

<a id="omega_vision.core.models.RecognitionAccount.allowed_transformations"></a>

#### allowed\_transformations: `tuple[str, ...]`

<a id="omega_vision.core.models.RecognitionAccount.turtle_reconstruction_fit"></a>

#### turtle\_reconstruction\_fit: `float | None`

<a id="omega_vision.core.models.RecognitionAccount.residual_score"></a>

#### residual\_score: `float | None`

<a id="omega_vision.core.models.RecognitionAccount.supporting_evidence_ids"></a>

#### supporting\_evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.RecognitionAccount.contradicting_evidence_ids"></a>

#### contradicting\_evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.RecognitionAccount.rival_proposal_ids"></a>

#### rival\_proposal\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.RecognitionAccount.calibrated_confidence"></a>

#### calibrated\_confidence: `float`

<a id="omega_vision.core.models.RecognitionAccount.decision_confidence"></a>

#### decision\_confidence: `float | None`

<a id="omega_vision.core.models.RecognitionAccount.decision_outcome"></a>

#### decision\_outcome: `bool | None`

<a id="omega_vision.core.models.RecognitionAccount.decision_source"></a>

#### decision\_source: `str`

<a id="omega_vision.core.models.RecognitionAccount.provenance"></a>

#### provenance: `tuple[ProvenanceRef, ...]`

<a id="omega_vision.core.models.RecognitionAccount.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.RecognitionAccount.create"></a>

#### create

```python
@classmethod
def create(cls, *, candidate_id: str, stored_identity_id: str | None,
           **values: Any) -> "RecognitionAccount"
```

<a id="omega_vision.core.models.ObjectChange"></a>

## ObjectChange Objects

```python
@dataclass(frozen=True)
class ObjectChange()
```

<a id="omega_vision.core.models.ObjectChange.change_id"></a>

#### change\_id: `str`

<a id="omega_vision.core.models.ObjectChange.kind"></a>

#### kind: `str`

<a id="omega_vision.core.models.ObjectChange.before_identity_ids"></a>

#### before\_identity\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.ObjectChange.after_candidate_ids"></a>

#### after\_candidate\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.ObjectChange.properties"></a>

#### properties: `Mapping[str, Any]`

<a id="omega_vision.core.models.ObjectChange.evidence_ids"></a>

#### evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.ObjectChange.provenance"></a>

#### provenance: `tuple[ProvenanceRef, ...]`

<a id="omega_vision.core.models.ObjectChange.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.ObjectChange.create"></a>

#### create

```python
@classmethod
def create(
    cls,
    *,
    kind: str,
    before_identity_ids: tuple[str, ...] = (),
    after_candidate_ids: tuple[str, ...] = (),
    properties: Mapping[str, Any] | None = None,
    evidence_ids: tuple[str, ...] = (),
    provenance: tuple[ProvenanceRef, ...] = ()
) -> "ObjectChange"
```

<a id="omega_vision.core.models.EncounterRecord"></a>

## EncounterRecord Objects

```python
@dataclass(frozen=True)
class EncounterRecord()
```

<a id="omega_vision.core.models.EncounterRecord.encounter_id"></a>

#### encounter\_id: `str`

<a id="omega_vision.core.models.EncounterRecord.observation_id"></a>

#### observation\_id: `str`

<a id="omega_vision.core.models.EncounterRecord.action_tree_node"></a>

#### action\_tree\_node: `str`

<a id="omega_vision.core.models.EncounterRecord.object_identity_id"></a>

#### object\_identity\_id: `str | None`

<a id="omega_vision.core.models.EncounterRecord.candidate_identity_id"></a>

#### candidate\_identity\_id: `str | None`

<a id="omega_vision.core.models.EncounterRecord.instance"></a>

#### instance: `InstanceParameters`

<a id="omega_vision.core.models.EncounterRecord.matched_properties"></a>

#### matched\_properties: `tuple[str, ...]`

<a id="omega_vision.core.models.EncounterRecord.changed_properties"></a>

#### changed\_properties: `Mapping[str, Any]`

<a id="omega_vision.core.models.EncounterRecord.turtle_programs"></a>

#### turtle\_programs: `tuple[TurtleProgramRef, ...]`

<a id="omega_vision.core.models.EncounterRecord.reconstruction_artifacts"></a>

#### reconstruction\_artifacts: `tuple[ArtifactRef, ...]`

<a id="omega_vision.core.models.EncounterRecord.residual_ids"></a>

#### residual\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.EncounterRecord.confidence"></a>

#### confidence: `float`

<a id="omega_vision.core.models.EncounterRecord.evidence_ids"></a>

#### evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.EncounterRecord.previous_encounter_id"></a>

#### previous\_encounter\_id: `str | None`

<a id="omega_vision.core.models.EncounterRecord.next_encounter_id"></a>

#### next\_encounter\_id: `str | None`

<a id="omega_vision.core.models.EncounterRecord.provenance"></a>

#### provenance: `tuple[ProvenanceRef, ...]`

<a id="omega_vision.core.models.EncounterRecord.deterministic_hash"></a>

#### deterministic\_hash: `str`

<a id="omega_vision.core.models.EncounterRecord.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.EncounterRecord.create"></a>

#### create

```python
@classmethod
def create(cls,
           *,
           observation_id: str,
           action_tree_node: str,
           object_identity_id: str | None = None,
           candidate_identity_id: str | None = None,
           instance: InstanceParameters | None = None,
           provenance: tuple[ProvenanceRef, ...] = (),
           **changes: Any) -> "EncounterRecord"
```

<a id="omega_vision.core.models.NormalizedResult"></a>

## NormalizedResult Objects

```python
@dataclass(frozen=True)
class NormalizedResult()
```

Backend-neutral return shape used by all providers.

<a id="omega_vision.core.models.NormalizedResult.value"></a>

#### value: `Any`

<a id="omega_vision.core.models.NormalizedResult.mode"></a>

#### mode: `ExecutionMode`

<a id="omega_vision.core.models.NormalizedResult.source_refs"></a>

#### source\_refs: `tuple[str, ...]`

<a id="omega_vision.core.models.NormalizedResult.evidence"></a>

#### evidence: `tuple[str, ...]`

<a id="omega_vision.core.models.NormalizedResult.metadata"></a>

#### metadata: `Mapping[str, Any]`

<a id="omega_vision.core.models.CandidateObject"></a>

## CandidateObject Objects

```python
@dataclass(frozen=True)
class CandidateObject()
```

<a id="omega_vision.core.models.CandidateObject.candidate_id"></a>

#### candidate\_id: `str`

<a id="omega_vision.core.models.CandidateObject.observation_id"></a>

#### observation\_id: `str`

<a id="omega_vision.core.models.CandidateObject.domain"></a>

#### domain: `str`

<a id="omega_vision.core.models.CandidateObject.provider"></a>

#### provider: `"ArtifactProviderProtocol"`

<a id="omega_vision.core.models.CandidateObject.region_ref"></a>

#### region\_ref: `str | None`

<a id="omega_vision.core.models.CandidateObject.provenance"></a>

#### provenance: `tuple[str, ...]`

<a id="omega_vision.core.models.CandidateObject.part"></a>

#### part

```python
def part(name: str) -> NormalizedResult
```

<a id="omega_vision.core.models.ResidualCandidate"></a>

## ResidualCandidate Objects

```python
@dataclass(frozen=True)
class ResidualCandidate()
```

<a id="omega_vision.core.models.ResidualCandidate.residual_id"></a>

#### residual\_id: `str`

<a id="omega_vision.core.models.ResidualCandidate.source_candidate_id"></a>

#### source\_candidate\_id: `str`

<a id="omega_vision.core.models.ResidualCandidate.disposition"></a>

#### disposition: `ResidualDisposition`

<a id="omega_vision.core.models.ResidualCandidate.residual_length"></a>

#### residual\_length: `float`

<a id="omega_vision.core.models.ResidualCandidate.structured"></a>

#### structured: `bool`

<a id="omega_vision.core.models.ResidualCandidate.recurrence_count"></a>

#### recurrence\_count: `int`

<a id="omega_vision.core.models.ResidualCandidate.prediction_gain"></a>

#### prediction\_gain: `float`

<a id="omega_vision.core.models.ResidualCandidate.provenance"></a>

#### provenance: `tuple[str, ...]`

<a id="omega_vision.core.models.ResidualCandidate.create"></a>

#### create

```python
@classmethod
def create(cls,
           *,
           source_candidate_id: str,
           disposition: ResidualDisposition,
           residual_length: float,
           provenance: tuple[str, ...] = (),
           **values: Any) -> "ResidualCandidate"
```

<a id="omega_vision.core.models.CommittedAtom"></a>

## CommittedAtom Objects

```python
@dataclass(frozen=True)
class CommittedAtom()
```

<a id="omega_vision.core.models.CommittedAtom.handle"></a>

#### handle: `str`

<a id="omega_vision.core.models.CommittedAtom.atom_type"></a>

#### atom\_type: `str`

<a id="omega_vision.core.models.CommittedAtom.payload"></a>

#### payload: `Mapping[str, Any]`

<a id="omega_vision.core.models.CommittedAtom.confidence"></a>

#### confidence: `float`

<a id="omega_vision.core.models.CommittedAtom.provenance"></a>

#### provenance: `tuple[str, ...]`

<a id="omega_vision.core.models.CommittedAtom.lifecycle_state"></a>

#### lifecycle\_state: `str`

<a id="omega_vision.core.models.ConfidenceHistoryRecord"></a>

## ConfidenceHistoryRecord Objects

```python
@dataclass(frozen=True)
class ConfidenceHistoryRecord()
```

<a id="omega_vision.core.models.ConfidenceHistoryRecord.sequence"></a>

#### sequence: `int`

<a id="omega_vision.core.models.ConfidenceHistoryRecord.handle"></a>

#### handle: `str`

<a id="omega_vision.core.models.ConfidenceHistoryRecord.confidence"></a>

#### confidence: `float`

<a id="omega_vision.core.models.ConfidenceHistoryRecord.lifecycle_state"></a>

#### lifecycle\_state: `str`

<a id="omega_vision.core.models.ConfidenceHistoryRecord.event"></a>

#### event: `str`

<a id="omega_vision.core.models.ConfidenceHistoryRecord.reference_id"></a>

#### reference\_id: `str | None`

<a id="omega_vision.core.models.TransitionRule"></a>

## TransitionRule Objects

```python
@dataclass(frozen=True)
class TransitionRule()
```

<a id="omega_vision.core.models.TransitionRule.rule_id"></a>

#### rule\_id: `str`

<a id="omega_vision.core.models.TransitionRule.preconditions"></a>

#### preconditions: `tuple[Any, ...]`

<a id="omega_vision.core.models.TransitionRule.action_or_event"></a>

#### action\_or\_event: `Any`

<a id="omega_vision.core.models.TransitionRule.predicted_effects"></a>

#### predicted\_effects: `tuple[Any, ...]`

<a id="omega_vision.core.models.TransitionRule.provenance"></a>

#### provenance: `tuple[str, ...]`

<a id="omega_vision.core.models.TransitionRule.assumptions"></a>

#### assumptions: `tuple[str, ...]`

<a id="omega_vision.core.models.TransitionRule.critiques"></a>

#### critiques: `tuple[str, ...]`

<a id="omega_vision.core.models.TransitionRule.supporting_evidence_ids"></a>

#### supporting\_evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.TransitionRule.contradicting_evidence_ids"></a>

#### contradicting\_evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.TransitionRule.rival_rule_ids"></a>

#### rival\_rule\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.TransitionRule.bootstrap_probability"></a>

#### bootstrap\_probability: `float`

<a id="omega_vision.core.models.TransitionRule.calibrated_probability"></a>

#### calibrated\_probability: `float | None`

<a id="omega_vision.core.models.TransitionRule.probability_source"></a>

#### probability\_source: `str`

<a id="omega_vision.core.models.TransitionRule.coverage"></a>

#### coverage: `float`

<a id="omega_vision.core.models.TransitionRule.applicability_precision"></a>

#### applicability\_precision: `float | None`

<a id="omega_vision.core.models.TransitionRule.prediction_attempts"></a>

#### prediction\_attempts: `int`

<a id="omega_vision.core.models.TransitionRule.prediction_successes"></a>

#### prediction\_successes: `int`

<a id="omega_vision.core.models.TransitionRule.prediction_score_total"></a>

#### prediction\_score\_total: `float`

<a id="omega_vision.core.models.TransitionRule.prediction_history"></a>

#### prediction\_history: `tuple[str, ...]`

<a id="omega_vision.core.models.ActionRecommendation"></a>

## ActionRecommendation Objects

```python
@dataclass(frozen=True)
class ActionRecommendation()
```

<a id="omega_vision.core.models.ActionRecommendation.recommendation_id"></a>

#### recommendation\_id: `str`

<a id="omega_vision.core.models.ActionRecommendation.rule_id"></a>

#### rule\_id: `str`

<a id="omega_vision.core.models.ActionRecommendation.source_state_id"></a>

#### source\_state\_id: `str`

<a id="omega_vision.core.models.ActionRecommendation.recommended_action"></a>

#### recommended\_action: `Any`

<a id="omega_vision.core.models.ActionRecommendation.attempted_action"></a>

#### attempted\_action: `Any`

<a id="omega_vision.core.models.ActionRecommendation.created_sequence"></a>

#### created\_sequence: `int`

<a id="omega_vision.core.models.ActionRecommendation.rival_rule_ids"></a>

#### rival\_rule\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.ActionRecommendation.available_evidence_ids"></a>

#### available\_evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.ActionRecommendation.assumptions"></a>

#### assumptions: `tuple[str, ...]`

<a id="omega_vision.core.models.ActionRecommendation.critiques"></a>

#### critiques: `tuple[str, ...]`

<a id="omega_vision.core.models.ActionRecommendation.probability"></a>

#### probability: `float | None`

<a id="omega_vision.core.models.ActionRecommendation.probability_source"></a>

#### probability\_source: `str`

<a id="omega_vision.core.models.ActionRecommendation.prediction_id"></a>

#### prediction\_id: `str | None`

<a id="omega_vision.core.models.ActionRecommendation.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.ActionRecommendation.create"></a>

#### create

```python
@classmethod
def create(cls, **values: Any) -> "ActionRecommendation"
```

<a id="omega_vision.core.models.PredictionRecord"></a>

## PredictionRecord Objects

```python
@dataclass(frozen=True)
class PredictionRecord()
```

<a id="omega_vision.core.models.PredictionRecord.prediction_id"></a>

#### prediction\_id: `str`

<a id="omega_vision.core.models.PredictionRecord.rule_id"></a>

#### rule\_id: `str`

<a id="omega_vision.core.models.PredictionRecord.source_state_id"></a>

#### source\_state\_id: `str`

<a id="omega_vision.core.models.PredictionRecord.predicted_effects"></a>

#### predicted\_effects: `tuple[Any, ...]`

<a id="omega_vision.core.models.PredictionRecord.created_sequence"></a>

#### created\_sequence: `int`

<a id="omega_vision.core.models.PredictionRecord.available_evidence_ids"></a>

#### available\_evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.PredictionRecord.rule_assumptions"></a>

#### rule\_assumptions: `tuple[str, ...]`

<a id="omega_vision.core.models.PredictionRecord.rule_critiques"></a>

#### rule\_critiques: `tuple[str, ...]`

<a id="omega_vision.core.models.PredictionRecord.rule_probability"></a>

#### rule\_probability: `float | None`

<a id="omega_vision.core.models.PredictionRecord.rule_probability_source"></a>

#### rule\_probability\_source: `str`

<a id="omega_vision.core.models.PredictionRecord.outcome_sequence"></a>

#### outcome\_sequence: `int | None`

<a id="omega_vision.core.models.PredictionRecord.outcome"></a>

#### outcome: `Any`

<a id="omega_vision.core.models.PredictionRecord.grade"></a>

#### grade: `float | None`

<a id="omega_vision.core.models.PredictionGradeRecord"></a>

## PredictionGradeRecord Objects

```python
@dataclass(frozen=True)
class PredictionGradeRecord()
```

Immutable outcome and grade linked to an earlier prediction.

<a id="omega_vision.core.models.PredictionGradeRecord.prediction_id"></a>

#### prediction\_id: `str`

<a id="omega_vision.core.models.PredictionGradeRecord.rule_id"></a>

#### rule\_id: `str`

<a id="omega_vision.core.models.PredictionGradeRecord.outcome_sequence"></a>

#### outcome\_sequence: `int`

<a id="omega_vision.core.models.PredictionGradeRecord.outcome"></a>

#### outcome: `Any`

<a id="omega_vision.core.models.PredictionGradeRecord.grade"></a>

#### grade: `float | None`

<a id="omega_vision.core.models.PredictionGradeRecord.status"></a>

#### status: `str`

<a id="omega_vision.core.models.PredictionGradeRecord.evidence"></a>

#### evidence: `tuple[str, ...]`

<a id="omega_vision.core.models.PredictionGradeRecord.evidence_record_ids"></a>

#### evidence\_record\_ids: `tuple[str, ...]`

<a id="omega_vision.core.models.PredictionGradeRecord.prior_probability"></a>

#### prior\_probability: `float | None`

<a id="omega_vision.core.models.PredictionGradeRecord.calibrated_probability"></a>

#### calibrated\_probability: `float | None`

<a id="omega_vision.core.models.PredictionGradeRecord.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.core.models.ArtifactProviderProtocol"></a>

## ArtifactProviderProtocol Objects

```python
class ArtifactProviderProtocol()
```

<a id="omega_vision.core.models.ArtifactProviderProtocol.get_candidate_part"></a>

#### get\_candidate\_part

```python
def get_candidate_part(candidate: CandidateObject,
                       name: str) -> NormalizedResult
```

<a id="omega_vision.core.prediction"></a>

# omega\_vision.core.prediction

<a id="omega_vision.core.prediction.RuleStore"></a>

## RuleStore Objects

```python
class RuleStore()
```

Exact-identity rule registry with caller-supplied domain execution.

<a id="omega_vision.core.prediction.RuleStore.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

<a id="omega_vision.core.prediction.RuleStore.store"></a>

#### store

```python
def store(rule: TransitionRule) -> TransitionRule
```

<a id="omega_vision.core.prediction.RuleStore.get"></a>

#### get

```python
def get(rule_id: str) -> TransitionRule
```

<a id="omega_vision.core.prediction.RuleStore.rules"></a>

#### rules

```python
def rules() -> tuple[TransitionRule, ...]
```

<a id="omega_vision.core.prediction.RuleStore.record_prediction_grade"></a>

#### record\_prediction\_grade

```python
def record_prediction_grade(
    rule_id: str,
    *,
    prediction_id: str,
    grade: float,
    supporting_evidence_ids: tuple[str, ...] = (),
    contradicting_evidence_ids: tuple[str, ...] = ()
) -> TransitionRule
```

Refine one rule only from an independently graded prior prediction.

<a id="omega_vision.core.prediction.RuleStore.applicable"></a>

#### applicable

```python
def applicable(rule_id: str, state: Any,
               checker: Callable[[TransitionRule, Any], bool]) -> bool
```

<a id="omega_vision.core.prediction.RuleStore.apply"></a>

#### apply

```python
def apply(rule_id: str, state: Any, executor: Callable[[TransitionRule, Any],
                                                       Any]) -> Any
```

<a id="omega_vision.core.prediction.PredictionLedger"></a>

## PredictionLedger Objects

```python
class PredictionLedger()
```

Append-only prediction records enforcing predict-before-check.

<a id="omega_vision.core.prediction.PredictionLedger.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

<a id="omega_vision.core.prediction.PredictionLedger.record"></a>

#### record

```python
def record(prediction: PredictionRecord) -> PredictionRecord
```

<a id="omega_vision.core.prediction.PredictionLedger.grade"></a>

#### grade

```python
def grade(prediction_id: str, *, outcome_sequence: int, outcome: Any,
          grade: float | None) -> PredictionRecord
```

<a id="omega_vision.core.prediction.PredictionLedger.get"></a>

#### get

```python
def get(prediction_id: str) -> PredictionRecord
```

<a id="omega_vision.core.prediction.PredictionLedger.records"></a>

#### records

```python
def records() -> tuple[PredictionRecord, ...]
```

<a id="omega_vision.core.recognition"></a>

# omega\_vision.core.recognition

<a id="omega_vision.core.recognition.PartialVisibilityCompletion"></a>

## PartialVisibilityCompletion Objects

```python
@dataclass(frozen=True)
class PartialVisibilityCompletion()
```

A reconstructed instance that keeps inferred and observed data distinct.

<a id="omega_vision.core.recognition.PartialVisibilityCompletion.candidate_id"></a>

#### candidate\_id: `str`

<a id="omega_vision.core.recognition.PartialVisibilityCompletion.stored_identity_id"></a>

#### stored\_identity\_id: `str`

<a id="omega_vision.core.recognition.PartialVisibilityCompletion.observed"></a>

#### observed: `InstanceParameters`

<a id="omega_vision.core.recognition.PartialVisibilityCompletion.completed"></a>

#### completed: `InstanceParameters`

<a id="omega_vision.core.recognition.PartialVisibilityCompletion.inferred_fields"></a>

#### inferred\_fields: `tuple[str, ...]`

<a id="omega_vision.core.recognition.PartialVisibilityCompletion.proposal_id"></a>

#### proposal\_id: `str`

<a id="omega_vision.core.recognition.PartialVisibilityCompletion.evidence_ids"></a>

#### evidence\_ids: `tuple[str, ...]`

<a id="omega_vision.core.recognition.InstanceMatcher"></a>

## InstanceMatcher Objects

```python
class InstanceMatcher()
```

Generate advisory correspondence proposals from normalized instances.

<a id="omega_vision.core.recognition.InstanceMatcher.change_transformation"></a>

#### change\_transformation

```python
@staticmethod
def change_transformation(field: str) -> str
```

<a id="omega_vision.core.recognition.InstanceMatcher.compare"></a>

#### compare

```python
def compare(
    *,
    candidate_id: str,
    current: InstanceParameters,
    stored_identity_id: str,
    stored: InstanceParameters,
    provenance: tuple[ProvenanceRef, ...] = ()
) -> MatchProposal
```

<a id="omega_vision.core.recognition.InstanceMatcher.proposals"></a>

#### proposals

```python
def proposals(
    *,
    candidate_id: str,
    current: InstanceParameters,
    stored: Mapping[str, InstanceParameters],
    provenance: tuple[ProvenanceRef, ...] = (),
    retrieval_scores: Mapping[str, float] | None = None,
    retrieval_source: str | None = None,
    calibration_policy: RecognitionCalibrationPolicy | None = None
) -> tuple[MatchProposal, ...]
```

<a id="omega_vision.core.recognition.InstanceMatcher.recognition_account"></a>

#### recognition\_account

```python
def recognition_account(
        *,
        candidate_id: str,
        proposals: tuple[MatchProposal, ...],
        selected_identity_id: str | None = None,
        decision_source: str = "unresolved") -> RecognitionAccount
```

<a id="omega_vision.core.recognition.RecognitionSession"></a>

## RecognitionSession Objects

```python
class RecognitionSession()
```

Persist unresolved proposals between a candidate and known encounter histories.

<a id="omega_vision.core.recognition.RecognitionSession.__init__"></a>

#### \_\_init\_\_

```python
def __init__(store: SymbolicStore,
             matcher: InstanceMatcher | None = None) -> None
```

<a id="omega_vision.core.recognition.RecognitionSession.latest_known_instances"></a>

#### latest\_known\_instances

```python
def latest_known_instances() -> dict[str, InstanceParameters]
```

<a id="omega_vision.core.recognition.RecognitionSession.complete_partial"></a>

#### complete\_partial

```python
def complete_partial(encounter_id: str,
                     stored_identity_id: str) -> PartialVisibilityCompletion
```

Complete an occluded encounter from one prior durable identity form.

<a id="omega_vision.core.recognition.RecognitionSession.propose"></a>

#### propose

```python
def propose(encounter_id: str,
            *,
            retrieval_scores: Mapping[str, float] | None = None,
            retrieval_source: str | None = None) -> tuple[MatchProposal, ...]
```

<a id="omega_vision.core.recognition.RecognitionSession.unresolved_account"></a>

#### unresolved\_account

```python
def unresolved_account(candidate_id: str) -> RecognitionAccount | None
```

<a id="omega_vision.core.recognition.CorrespondenceEvidenceBuilder"></a>

## CorrespondenceEvidenceBuilder Objects

```python
class CorrespondenceEvidenceBuilder()
```

Create attributable signed evidence from a proposal's property explanation.

<a id="omega_vision.core.recognition.CorrespondenceEvidenceBuilder.build"></a>

#### build

```python
def build(proposal: MatchProposal,
          *,
          source: ProvenanceRef,
          created_sequence: int = 0) -> tuple[EvidenceRecord, ...]
```

<a id="omega_vision.core.recognition.EncounterChangeSession"></a>

## EncounterChangeSession Objects

```python
class EncounterChangeSession()
```

Persist correspondences, evidence, and changes across two observations.

<a id="omega_vision.core.recognition.EncounterChangeSession.__init__"></a>

#### \_\_init\_\_

```python
def __init__(store: SymbolicStore,
             matcher: InstanceMatcher | None = None) -> None
```

<a id="omega_vision.core.recognition.EncounterChangeSession.detect"></a>

#### detect

```python
def detect(
    previous_observation_id: str, current_observation_id: str
) -> tuple[
        tuple[MatchProposal, ...],
        tuple[ObjectChange, ...],
        tuple[ResidualCandidate, ...],
]
```

<a id="omega_vision.core.recognition.StructuralCorrespondenceInferer"></a>

## StructuralCorrespondenceInferer Objects

```python
class StructuralCorrespondenceInferer()
```

Infer only exact one-to-one, split, or merge cell-set correspondences.

<a id="omega_vision.core.recognition.StructuralCorrespondenceInferer.infer"></a>

#### infer

```python
def infer(previous: Mapping[str, Any],
          current: Mapping[str, Any]) -> dict[str, tuple[str, ...]]
```

<a id="omega_vision.core.recognition.ResidualAnalyzer"></a>

## ResidualAnalyzer Objects

```python
class ResidualAnalyzer()
```

Separate unexplained proposal structure from recognized transformations.

<a id="omega_vision.core.recognition.ResidualAnalyzer.__init__"></a>

#### \_\_init\_\_

```python
def __init__(gate: ResidualGate | None = None) -> None
```

<a id="omega_vision.core.recognition.ResidualAnalyzer.from_proposal"></a>

#### from\_proposal

```python
def from_proposal(proposal: MatchProposal) -> tuple[ResidualCandidate, ...]
```

<a id="omega_vision.core.recognition.TurtleReconstructionEvidenceBuilder"></a>

## TurtleReconstructionEvidenceBuilder Objects

```python
class TurtleReconstructionEvidenceBuilder()
```

Represent an exact or residual Turtle reconstruction fit as signed evidence.

<a id="omega_vision.core.recognition.TurtleReconstructionEvidenceBuilder.build"></a>

#### build

```python
def build(*,
          identity_id: str,
          fit: FitResult,
          source: ProvenanceRef,
          artifact_id: str | None = None,
          created_sequence: int = 0) -> EvidenceRecord
```

<a id="omega_vision.core.recognition.ChangeDetector"></a>

## ChangeDetector Objects

```python
class ChangeDetector()
```

Classify resolved before/after correspondences into semantic changes.

<a id="omega_vision.core.recognition.ChangeDetector.PROPERTY_KINDS"></a>

#### PROPERTY\_KINDS

<a id="omega_vision.core.recognition.ChangeDetector.detect"></a>

#### detect

```python
def detect(
    *,
    proposals: Mapping[str, MatchProposal],
    correspondence: Mapping[str, tuple[str, ...]],
    before_identity_ids: tuple[str, ...],
    after_candidate_ids: tuple[str, ...],
    provenance: tuple[ProvenanceRef, ...] = ()
) -> tuple[ObjectChange, ...]
```

<a id="omega_vision.core.recognition.RegistryCorrespondenceAuthority"></a>

## RegistryCorrespondenceAuthority Objects

```python
class RegistryCorrespondenceAuthority()
```

Apply an explicit registry selection only when attributable evidence exists.

<a id="omega_vision.core.recognition.RegistryCorrespondenceAuthority.__init__"></a>

#### \_\_init\_\_

```python
def __init__(writer: SingleWriter | None, action_tree_store: object) -> None
```

<a id="omega_vision.core.recognition.RegistryCorrespondenceAuthority.accept"></a>

#### accept

```python
def accept(*, candidate_id: str, selected_identity_id: str,
           proposals: tuple[MatchProposal,
                            ...], evidence: tuple[EvidenceRecord,
                                                  ...], encounter_id: str,
           decision_id: str, decision_source: str) -> RecognitionAccount
```

<a id="omega_vision.core.recognition.RegistryCorrespondenceAuthority.reject"></a>

#### reject

```python
def reject(
    *,
    candidate_id: str,
    selected_identity_id: str,
    proposals: tuple[MatchProposal, ...],
    encounter_id: str,
    decision_id: str,
    decision_source: str,
    evidence_ids: tuple[str, ...] = ()
) -> RecognitionAccount
```

<a id="omega_vision.core.recognition.RegistryCorrespondenceAuthority.reverse"></a>

#### reverse

```python
def reverse(*, identity_id: str, encounter_id: str, decision_id: str,
            evidence_ids: tuple[str, ...]) -> None
```

<a id="omega_vision.core.store"></a>

# omega\_vision.core.store

<a id="omega_vision.core.store.SemanticStoreBackend"></a>

## SemanticStoreBackend Objects

```python
class SemanticStoreBackend(Protocol)
```

Minimal exact-record boundary implemented by Prolog or AtomSpace stores.

<a id="omega_vision.core.store.SemanticStoreBackend.write_once"></a>

#### write\_once

```python
def write_once(namespace: str, record_id: str, value: Any) -> Any
```

<a id="omega_vision.core.store.SemanticStoreBackend.get"></a>

#### get

```python
def get(namespace: str, record_id: str) -> Any | None
```

<a id="omega_vision.core.store.SemanticStoreBackend.values"></a>

#### values

```python
def values(namespace: str) -> tuple[Any, ...]
```

<a id="omega_vision.core.store.InMemorySemanticBackend"></a>

## InMemorySemanticBackend Objects

```python
class InMemorySemanticBackend()
```

Deterministic reference backend used by tests and local composition.

<a id="omega_vision.core.store.InMemorySemanticBackend.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

<a id="omega_vision.core.store.InMemorySemanticBackend.write_once"></a>

#### write\_once

```python
def write_once(namespace: str, record_id: str, value: Any) -> Any
```

<a id="omega_vision.core.store.InMemorySemanticBackend.get"></a>

#### get

```python
def get(namespace: str, record_id: str) -> Any | None
```

<a id="omega_vision.core.store.InMemorySemanticBackend.values"></a>

#### values

```python
def values(namespace: str) -> tuple[Any, ...]
```

<a id="omega_vision.core.store.ArtifactIndex"></a>

## ArtifactIndex Objects

```python
class ArtifactIndex()
```

Exact artifact lookup by stable ID and semantic artifact type.

<a id="omega_vision.core.store.ArtifactIndex.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

<a id="omega_vision.core.store.ArtifactIndex.register"></a>

#### register

```python
def register(artifact: ArtifactRef) -> ArtifactRef
```

<a id="omega_vision.core.store.ArtifactIndex.get"></a>

#### get

```python
def get(artifact_id: str) -> ArtifactRef | None
```

<a id="omega_vision.core.store.ArtifactIndex.by_type"></a>

#### by\_type

```python
def by_type(artifact_type: str) -> tuple[ArtifactRef, ...]
```

<a id="omega_vision.core.store.SymbolicStore"></a>

## SymbolicStore Objects

```python
class SymbolicStore()
```

Backend-neutral facade for exact Phase 2 semantic records.

Similarity indexes may propose identifiers to query here, but only exact
stable identifiers address or commit records through this boundary.

<a id="omega_vision.core.store.SymbolicStore.__init__"></a>

#### \_\_init\_\_

```python
def __init__(backend: SemanticStoreBackend) -> None
```

<a id="omega_vision.core.store.SymbolicStore.put_observation"></a>

#### put\_observation

```python
def put_observation(value: Observation) -> Observation
```

<a id="omega_vision.core.store.SymbolicStore.put_encounter"></a>

#### put\_encounter

```python
def put_encounter(value: EncounterRecord) -> EncounterRecord
```

<a id="omega_vision.core.store.SymbolicStore.put_recognition"></a>

#### put\_recognition

```python
def put_recognition(value: RecognitionAccount) -> RecognitionAccount
```

<a id="omega_vision.core.store.SymbolicStore.put_match_proposal"></a>

#### put\_match\_proposal

```python
def put_match_proposal(value: MatchProposal) -> MatchProposal
```

<a id="omega_vision.core.store.SymbolicStore.put_evidence"></a>

#### put\_evidence

```python
def put_evidence(value: EvidenceRecord) -> EvidenceRecord
```

<a id="omega_vision.core.store.SymbolicStore.put_object_change"></a>

#### put\_object\_change

```python
def put_object_change(value: ObjectChange) -> ObjectChange
```

<a id="omega_vision.core.store.SymbolicStore.put_residual"></a>

#### put\_residual

```python
def put_residual(value: ResidualCandidate) -> ResidualCandidate
```

<a id="omega_vision.core.store.SymbolicStore.put_artifact"></a>

#### put\_artifact

```python
def put_artifact(value: ArtifactRef) -> ArtifactRef
```

<a id="omega_vision.core.store.SymbolicStore.put_turtle"></a>

#### put\_turtle

```python
def put_turtle(value: TurtleProgramRef) -> TurtleProgramRef
```

<a id="omega_vision.core.store.SymbolicStore.put_atom"></a>

#### put\_atom

```python
def put_atom(value: CommittedAtom) -> CommittedAtom
```

<a id="omega_vision.core.store.SymbolicStore.put_confidence_history"></a>

#### put\_confidence\_history

```python
def put_confidence_history(
        value: ConfidenceHistoryRecord) -> ConfidenceHistoryRecord
```

<a id="omega_vision.core.store.SymbolicStore.put_identity_checkpoint"></a>

#### put\_identity\_checkpoint

```python
def put_identity_checkpoint(
        value: IdentityMemoryCheckpoint) -> IdentityMemoryCheckpoint
```

<a id="omega_vision.core.store.SymbolicStore.put_recognition_calibration"></a>

#### put\_recognition\_calibration

```python
def put_recognition_calibration(
        value: RecognitionCalibrationPolicy) -> RecognitionCalibrationPolicy
```

<a id="omega_vision.core.store.SymbolicStore.restore_identity_memory"></a>

#### restore\_identity\_memory

```python
def restore_identity_memory() -> "SymbolicMemory"
```

Restore the newest complete identity state stored by a SingleWriter.

<a id="omega_vision.core.store.SymbolicStore.compacted_snapshot"></a>

#### compacted\_snapshot

```python
def compacted_snapshot() -> dict[str, tuple[Any, ...]]
```

Export one self-contained checkpoint root plus all other semantic records.

<a id="omega_vision.core.store.SymbolicStore.put_prediction"></a>

#### put\_prediction

```python
def put_prediction(value: PredictionRecord) -> PredictionRecord
```

<a id="omega_vision.core.store.SymbolicStore.put_transition_rule"></a>

#### put\_transition\_rule

```python
def put_transition_rule(value: TransitionRule) -> TransitionRule
```

<a id="omega_vision.core.store.SymbolicStore.put_action_recommendation"></a>

#### put\_action\_recommendation

```python
def put_action_recommendation(
        value: ActionRecommendation) -> ActionRecommendation
```

<a id="omega_vision.core.store.SymbolicStore.put_prediction_grade"></a>

#### put\_prediction\_grade

```python
def put_prediction_grade(
        value: PredictionGradeRecord) -> PredictionGradeRecord
```

<a id="omega_vision.core.store.SymbolicStore.get"></a>

#### get

```python
def get(namespace: str, record_id: str) -> Any | None
```

<a id="omega_vision.core.store.SymbolicStore.values"></a>

#### values

```python
def values(namespace: str) -> tuple[Any, ...]
```

<a id="omega_vision.core.store.SymbolicStore.SNAPSHOT_NAMESPACES"></a>

#### SNAPSHOT\_NAMESPACES

<a id="omega_vision.core.store.SymbolicStore.snapshot"></a>

#### snapshot

```python
def snapshot() -> dict[str, tuple[Any, ...]]
```

Capture exact semantic records in deterministic replay order.

<a id="omega_vision.core.store.SymbolicStore.replay"></a>

#### replay

```python
def replay(snapshot: dict[str, tuple[Any, ...]]) -> "SymbolicStore"
```

Idempotently reconstruct this facade and its indexes from a snapshot.

<a id="omega_vision.core.store.SymbolicStore.hydrate"></a>

#### hydrate

```python
def hydrate() -> "SymbolicStore"
```

Populate facade indexes from records already present in the backend.

<a id="omega_vision.environments.environment_fixtures"></a>

# omega\_vision.environments.environment\_fixtures

<a id="omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures"></a>

## EnvironmentProgressionFixtures Objects

```python
@dataclass(frozen=True)
class EnvironmentProgressionFixtures()
```

<a id="omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures.rendered_arcade"></a>

#### rendered\_arcade: `tuple[PerceptionFixture, ...]`

<a id="omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures.fixed_camera"></a>

#### fixed\_camera: `tuple[PerceptionFixture, ...]`

<a id="omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures.top_down_manipulation"></a>

#### top\_down\_manipulation: `tuple[PerceptionFixture, ...]`

<a id="omega_vision.environments.environment_fixtures.EnvironmentProgressionFixtures.all"></a>

#### all

```python
def all() -> tuple[PerceptionFixture, ...]
```

<a id="omega_vision.environments.environment_fixtures.rendered_arcade_fixtures"></a>

#### rendered\_arcade\_fixtures

```python
def rendered_arcade_fixtures() -> tuple[PerceptionFixture, ...]
```

<a id="omega_vision.environments.environment_fixtures.fixed_camera_physics_fixtures"></a>

#### fixed\_camera\_physics\_fixtures

```python
def fixed_camera_physics_fixtures() -> tuple[PerceptionFixture, ...]
```

<a id="omega_vision.environments.environment_fixtures.top_down_manipulation_fixtures"></a>

#### top\_down\_manipulation\_fixtures

```python
def top_down_manipulation_fixtures() -> tuple[PerceptionFixture, ...]
```

<a id="omega_vision.environments.environment_fixtures.environment_progression_fixtures"></a>

#### environment\_progression\_fixtures

```python
def environment_progression_fixtures() -> EnvironmentProgressionFixtures
```

<a id="omega_vision.evaluation.acceptance"></a>

# omega\_vision.evaluation.acceptance

<a id="omega_vision.evaluation.acceptance.AcceptanceReport"></a>

## AcceptanceReport Objects

```python
@dataclass(frozen=True)
class AcceptanceReport()
```

<a id="omega_vision.evaluation.acceptance.AcceptanceReport.accepted"></a>

#### accepted: `bool`

<a id="omega_vision.evaluation.acceptance.AcceptanceReport.checks"></a>

#### checks: `Mapping[str, bool]`

<a id="omega_vision.evaluation.acceptance.AcceptanceReport.evidence"></a>

#### evidence: `Mapping[str, Any]`

<a id="omega_vision.evaluation.acceptance.AcceptanceReport.to_json"></a>

#### to\_json

```python
def to_json() -> str
```

<a id="omega_vision.evaluation.acceptance.AcceptanceReport.to_markdown"></a>

#### to\_markdown

```python
def to_markdown() -> str
```

<a id="omega_vision.evaluation.acceptance.build_acceptance_report"></a>

#### build\_acceptance\_report

```python
def build_acceptance_report(*, object_memory: Mapping[str, Any],
                            environment_progression: Mapping[str, Any],
                            phase3_learning: Mapping[str, Any],
                            test_result: str, commit: str) -> AcceptanceReport
```

<a id="omega_vision.evaluation.acceptance.write_acceptance_report"></a>

#### write\_acceptance\_report

```python
def write_acceptance_report(report: AcceptanceReport,
                            output_root: Path) -> tuple[Path, Path]
```

<a id="omega_vision.evaluation.benchmark"></a>

# omega\_vision.evaluation.benchmark

<a id="omega_vision.evaluation.benchmark.PerceptionFixture"></a>

## PerceptionFixture Objects

```python
@dataclass(frozen=True)
class PerceptionFixture()
```

<a id="omega_vision.evaluation.benchmark.PerceptionFixture.fixture_id"></a>

#### fixture\_id: `str`

<a id="omega_vision.evaluation.benchmark.PerceptionFixture.image"></a>

#### image: `Image.Image`

<a id="omega_vision.evaluation.benchmark.PerceptionFixture.expected_count"></a>

#### expected\_count: `int`

<a id="omega_vision.evaluation.benchmark.PerceptionFixture.degradation"></a>

#### degradation: `str`

<a id="omega_vision.evaluation.benchmark.PerceptionBenchmarkResult"></a>

## PerceptionBenchmarkResult Objects

```python
@dataclass(frozen=True)
class PerceptionBenchmarkResult()
```

<a id="omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.fixture_id"></a>

#### fixture\_id: `str`

<a id="omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.expected_count"></a>

#### expected\_count: `int`

<a id="omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.detected_count"></a>

#### detected\_count: `int`

<a id="omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.count_score"></a>

#### count\_score: `float`

<a id="omega_vision.evaluation.benchmark.PerceptionBenchmarkResult.degradation"></a>

#### degradation: `str`

<a id="omega_vision.evaluation.benchmark.RasterPerturbationGenerator"></a>

## RasterPerturbationGenerator Objects

```python
class RasterPerturbationGenerator()
```

Create deterministic modest-noise and partial-occlusion fixtures.

<a id="omega_vision.evaluation.benchmark.RasterPerturbationGenerator.__init__"></a>

#### \_\_init\_\_

```python
def __init__(seed: int = 0) -> None
```

<a id="omega_vision.evaluation.benchmark.RasterPerturbationGenerator.noise"></a>

#### noise

```python
def noise(image: Image.Image, probability: float = 0.05) -> Image.Image
```

<a id="omega_vision.evaluation.benchmark.RasterPerturbationGenerator.occlude"></a>

#### occlude

```python
def occlude(image: Image.Image, bounds: tuple[int, int, int,
                                              int]) -> Image.Image
```

<a id="omega_vision.evaluation.benchmark.RasterPerturbationGenerator.partial_occlusion_dataset"></a>

#### partial\_occlusion\_dataset

```python
def partial_occlusion_dataset(
        fixture_id: str, image: Image.Image, *, expected_count: int,
        occlusion: tuple[int, int, int, int]) -> tuple[PerceptionFixture, ...]
```

<a id="omega_vision.evaluation.benchmark.PerceptionBenchmarkRunner"></a>

## PerceptionBenchmarkRunner Objects

```python
class PerceptionBenchmarkRunner()
```

Evaluate any normalized image adapter against count-labeled fixtures.

<a id="omega_vision.evaluation.benchmark.PerceptionBenchmarkRunner.__init__"></a>

#### \_\_init\_\_

```python
def __init__(adapter: ImageAdapter) -> None
```

<a id="omega_vision.evaluation.benchmark.PerceptionBenchmarkRunner.run"></a>

#### run

```python
def run(
    fixtures: Iterable[PerceptionFixture]
) -> tuple[PerceptionBenchmarkResult, ...]
```

<a id="omega_vision.evaluation.benchmark.ProviderAblationRunner"></a>

## ProviderAblationRunner Objects

```python
class ProviderAblationRunner()
```

Run identical fixtures across named provider/mode adapter variants.

<a id="omega_vision.evaluation.benchmark.ProviderAblationRunner.__init__"></a>

#### \_\_init\_\_

```python
def __init__(adapters: Mapping[str, ImageAdapter]) -> None
```

<a id="omega_vision.evaluation.benchmark.ProviderAblationRunner.run"></a>

#### run

```python
def run(
    fixtures: Iterable[PerceptionFixture]
) -> Mapping[str, tuple[PerceptionBenchmarkResult, ...]]
```

<a id="omega_vision.evaluation.calibration"></a>

# omega\_vision.evaluation.calibration

<a id="omega_vision.evaluation.calibration.ReliabilityBin"></a>

## ReliabilityBin Objects

```python
@dataclass(frozen=True)
class ReliabilityBin()
```

<a id="omega_vision.evaluation.calibration.ReliabilityBin.lower"></a>

#### lower: `float`

<a id="omega_vision.evaluation.calibration.ReliabilityBin.upper"></a>

#### upper: `float`

<a id="omega_vision.evaluation.calibration.ReliabilityBin.count"></a>

#### count: `int`

<a id="omega_vision.evaluation.calibration.ReliabilityBin.mean_confidence"></a>

#### mean\_confidence: `float`

<a id="omega_vision.evaluation.calibration.ReliabilityBin.acceptance_rate"></a>

#### acceptance\_rate: `float`

<a id="omega_vision.evaluation.calibration.ReliabilityBin.brier_score"></a>

#### brier\_score: `float`

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationReport"></a>

## RecognitionCalibrationReport Objects

```python
@dataclass(frozen=True)
class RecognitionCalibrationReport()
```

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationReport.scope"></a>

#### scope: `str`

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationReport.sample_count"></a>

#### sample\_count: `int`

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationReport.brier_score"></a>

#### brier\_score: `float | None`

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationReport.bins"></a>

#### bins: `tuple[ReliabilityBin, ...]`

<a id="omega_vision.evaluation.calibration.CalibrationPoint"></a>

## CalibrationPoint Objects

```python
@dataclass(frozen=True)
class CalibrationPoint()
```

<a id="omega_vision.evaluation.calibration.CalibrationPoint.upper_confidence"></a>

#### upper\_confidence: `float`

<a id="omega_vision.evaluation.calibration.CalibrationPoint.probability"></a>

#### probability: `float`

<a id="omega_vision.evaluation.calibration.CalibrationPoint.sample_count"></a>

#### sample\_count: `int`

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationPolicy"></a>

## RecognitionCalibrationPolicy Objects

```python
@dataclass(frozen=True)
class RecognitionCalibrationPolicy()
```

Serializable monotone mapping learned from authoritative outcomes.

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.scope"></a>

#### scope: `str`

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.sample_count"></a>

#### sample\_count: `int`

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.points"></a>

#### points: `tuple[CalibrationPoint, ...]`

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.method"></a>

#### method: `str`

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.__post_init__"></a>

#### \_\_post\_init\_\_

```python
def __post_init__() -> None
```

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.calibrate"></a>

#### calibrate

```python
def calibrate(confidence: float) -> float
```

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.to_dict"></a>

#### to\_dict

```python
def to_dict() -> dict[str, Any]
```

<a id="omega_vision.evaluation.calibration.RecognitionCalibrationPolicy.from_dict"></a>

#### from\_dict

```python
@classmethod
def from_dict(cls, value: Mapping[str, Any]) -> "RecognitionCalibrationPolicy"
```

<a id="omega_vision.evaluation.calibration.RecognitionCalibrator"></a>

## RecognitionCalibrator Objects

```python
class RecognitionCalibrator()
```

Measure pre-decision confidence against later authority outcomes.

<a id="omega_vision.evaluation.calibration.RecognitionCalibrator.report"></a>

#### report

```python
def report(accounts: Iterable[RecognitionAccount],
           *,
           scope: str = "all",
           bin_count: int = 10) -> RecognitionCalibrationReport
```

<a id="omega_vision.evaluation.calibration.RecognitionCalibrator.fit"></a>

#### fit

```python
def fit(accounts: Iterable[RecognitionAccount], *,
        scope: str) -> RecognitionCalibrationPolicy
```

Fit a deterministic pool-adjacent-violators isotonic policy.

<a id="omega_vision.evaluation.calibration.RecognitionCalibrator.calibrated_report"></a>

#### calibrated\_report

```python
def calibrated_report(accounts: Iterable[RecognitionAccount],
                      policy: RecognitionCalibrationPolicy,
                      *,
                      bin_count: int = 10) -> RecognitionCalibrationReport
```

<a id="omega_vision.evaluation.recognition_benchmark"></a>

# omega\_vision.evaluation.recognition\_benchmark

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionFixture"></a>

## RecognitionFixture Objects

```python
@dataclass(frozen=True)
class RecognitionFixture()
```

One authority-labeled candidate and its complete identity rival set.

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionFixture.fixture_id"></a>

#### fixture\_id: `str`

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionFixture.scope"></a>

#### scope: `str`

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionFixture.current"></a>

#### current: `InstanceParameters`

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionFixture.stored"></a>

#### stored: `Mapping[str, InstanceParameters]`

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionFixture.accepted_identity_id"></a>

#### accepted\_identity\_id: `str | None`

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkResult"></a>

## RecognitionBenchmarkResult Objects

```python
@dataclass(frozen=True)
class RecognitionBenchmarkResult()
```

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkResult.fixture_id"></a>

#### fixture\_id: `str`

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkResult.scope"></a>

#### scope: `str`

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkResult.accounts"></a>

#### accounts: `tuple[RecognitionAccount, ...]`

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkRunner"></a>

## RecognitionBenchmarkRunner Objects

```python
class RecognitionBenchmarkRunner()
```

Exercise the real matcher and retain outcomes for every rival proposal.

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkRunner.__init__"></a>

#### \_\_init\_\_

```python
def __init__(matcher: InstanceMatcher | None = None) -> None
```

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkRunner.run"></a>

#### run

```python
def run(
    fixtures: tuple[RecognitionFixture, ...]
) -> tuple[RecognitionBenchmarkResult, ...]
```

<a id="omega_vision.evaluation.recognition_benchmark.RecognitionBenchmarkRunner.accounts"></a>

#### accounts

```python
@staticmethod
def accounts(results: tuple[RecognitionBenchmarkResult, ...],
             *,
             scope: str | None = None) -> tuple[RecognitionAccount, ...]
```

<a id="omega_vision.forms.forms"></a>

# omega\_vision.forms.forms

<a id="omega_vision.forms.forms.FitResult"></a>

## FitResult Objects

```python
@dataclass(frozen=True)
class FitResult()
```

<a id="omega_vision.forms.forms.FitResult.parameters"></a>

#### parameters: `dict[str, Any]`

<a id="omega_vision.forms.forms.FitResult.residual"></a>

#### residual: `float`

<a id="omega_vision.forms.forms.AbstractGenerativeForm"></a>

## AbstractGenerativeForm Objects

```python
class AbstractGenerativeForm(ABC)
```

Abstract typed contract for a generative form (Turtle/LOGO and later raster).

<a id="omega_vision.forms.forms.AbstractGenerativeForm.domain"></a>

#### domain: `str`

<a id="omega_vision.forms.forms.AbstractGenerativeForm.canonicalize"></a>

#### canonicalize

```python
@abstractmethod
def canonicalize() -> str
```

<a id="omega_vision.forms.forms.AbstractGenerativeForm.render"></a>

#### render

```python
@abstractmethod
def render(params: dict[str, Any] | None = None) -> Any
```

<a id="omega_vision.forms.forms.AbstractGenerativeForm.fit_instance"></a>

#### fit\_instance

```python
@abstractmethod
def fit_instance(candidate: Any) -> FitResult
```

<a id="omega_vision.forms.forms.AbstractGenerativeForm.distance"></a>

#### distance

```python
@abstractmethod
def distance(other: "AbstractGenerativeForm") -> float
```

<a id="omega_vision.forms.forms.GenerativeForm"></a>

## GenerativeForm Objects

```python
class GenerativeForm(AbstractGenerativeForm)
```

Canonical Turtle/LOGO generative form over the existing DSL program.

<a id="omega_vision.forms.forms.GenerativeForm.domain"></a>

#### domain

<a id="omega_vision.forms.forms.GenerativeForm.__init__"></a>

#### \_\_init\_\_

```python
def __init__(program: str,
             renderer: Any | None = None,
             swi_bridge: Any | None = None) -> None
```

<a id="omega_vision.forms.forms.GenerativeForm.canonicalize"></a>

#### canonicalize

```python
def canonicalize() -> str
```

<a id="omega_vision.forms.forms.GenerativeForm.render"></a>

#### render

```python
def render(params: dict[str, Any] | None = None) -> Any
```

<a id="omega_vision.forms.forms.GenerativeForm.fit_instance"></a>

#### fit\_instance

```python
def fit_instance(candidate: Any) -> FitResult
```

<a id="omega_vision.forms.forms.GenerativeForm.distance"></a>

#### distance

```python
def distance(other: AbstractGenerativeForm) -> float
```

<a id="omega_vision.forms.forms.GenerativeForm.description_length"></a>

#### description\_length

```python
def description_length() -> int
```

<a id="omega_vision.runtime.capture"></a>

# omega\_vision.runtime.capture

<a id="omega_vision.runtime.capture.standard_semantic_grid_observer"></a>

#### standard\_semantic\_grid\_observer

```python
def standard_semantic_grid_observer(*,
                                    learner_plugin: Any | None = None
                                    ) -> "SemanticGridCaptureObserver"
```

Compose the canonical live grid observer without coupling it to Phase 1.

<a id="omega_vision.runtime.capture.SemanticGridCaptureObserver"></a>

## SemanticGridCaptureObserver Objects

```python
class SemanticGridCaptureObserver()
```

External Arc3Runner observer that persists normalized Phase 2 records.

<a id="omega_vision.runtime.capture.SemanticGridCaptureObserver.__init__"></a>

#### \_\_init\_\_

```python
def __init__(adapter: GridAdapter,
             grid_selector: Callable[[Any], Any],
             symbolic_store: SymbolicStore | None = None,
             turtle_form_factory: Callable[[str], GenerativeForm]
             | None = None,
             identity_writer: SingleWriter | None = None,
             learner_plugin: Any | None = None) -> None
```

<a id="omega_vision.runtime.capture.SemanticGridCaptureObserver.authorization_options"></a>

#### authorization\_options

```python
def authorization_options() -> dict[str, tuple[str, ...]]
```

Return explicit friendly-identity choices for unresolved candidates.

<a id="omega_vision.runtime.capture.SemanticGridCaptureObserver.authorize_candidate"></a>

#### authorize\_candidate

```python
def authorize_candidate(
    *,
    candidate_id: str,
    selected_identity_id: str,
    decision_id: str,
    decision_source: str = "explicit_registry_selection"
) -> RecognitionAccount
```

Accept one pending proposal through the single identity writer.

<a id="omega_vision.runtime.capture.SemanticGridCaptureObserver.reject_candidate"></a>

#### reject\_candidate

```python
def reject_candidate(
    *,
    candidate_id: str,
    selected_identity_id: str,
    decision_id: str,
    decision_source: str = "explicit_registry_rejection"
) -> RecognitionAccount
```

Reject one pending friendly-identity proposal without calibrating it.

<a id="omega_vision.runtime.capture.SemanticGridCaptureObserver.before_action"></a>

#### before\_action

```python
def before_action(*, runner: Any, store: Any, node: Any, action: str,
                  data: Mapping[str, Any]) -> None
```

Record a learned-rule prediction before Arc3Runner observes the outcome.

<a id="omega_vision.runtime.capture.SemanticGridCaptureObserver.on_state_captured"></a>

#### on\_state\_captured

```python
def on_state_captured(*, runner: Any, store: Any, node: Any,
                      previous_node: Any, action: str | None,
                      data: Mapping[str, Any]) -> None
```

<a id="omega_vision.runtime.catalog"></a>

# omega\_vision.runtime.catalog

<a id="omega_vision.runtime.catalog.IdentityCatalogEntry"></a>

## IdentityCatalogEntry Objects

```python
@dataclass(frozen=True)
class IdentityCatalogEntry()
```

<a id="omega_vision.runtime.catalog.IdentityCatalogEntry.identity_id"></a>

#### identity\_id: `str`

<a id="omega_vision.runtime.catalog.IdentityCatalogEntry.instance"></a>

#### instance: `InstanceParameters`

<a id="omega_vision.runtime.catalog.IdentityCatalogEntry.registry_fact"></a>

#### registry\_fact: `str | None`

<a id="omega_vision.runtime.catalog.IdentityCatalogEntry.evidence"></a>

#### evidence: `tuple[EvidenceRecord, ...]`

<a id="omega_vision.runtime.catalog.IdentityCatalogEntry.provenance"></a>

#### provenance: `tuple[str, ...]`

<a id="omega_vision.runtime.catalog.SemanticIdentityCatalog"></a>

## SemanticIdentityCatalog Objects

```python
@dataclass(frozen=True)
class SemanticIdentityCatalog()
```

Portable durable identities for explicit reuse across examples.

<a id="omega_vision.runtime.catalog.SemanticIdentityCatalog.entries"></a>

#### entries: `tuple[IdentityCatalogEntry, ...]`

<a id="omega_vision.runtime.catalog.SemanticIdentityCatalog.source"></a>

#### source: `str`

<a id="omega_vision.runtime.catalog.SemanticIdentityCatalog.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.runtime.catalog.SemanticIdentityCatalog.from_store"></a>

#### from\_store

```python
@classmethod
def from_store(
        cls,
        store: SymbolicStore,
        *,
        source: str,
        registry: Mapping[str, str] | None = None
) -> "SemanticIdentityCatalog"
```

<a id="omega_vision.runtime.catalog.SemanticIdentityCatalog.to_json"></a>

#### to\_json

```python
def to_json() -> str
```

<a id="omega_vision.runtime.catalog.SemanticIdentityCatalog.from_json"></a>

#### from\_json

```python
@classmethod
def from_json(cls, value: str) -> "SemanticIdentityCatalog"
```

<a id="omega_vision.runtime.catalog.SemanticIdentityCatalog.import_into"></a>

#### import\_into

```python
def import_into(
        store: SymbolicStore,
        *,
        writer: SingleWriter | None = None) -> tuple[EncounterRecord, ...]
```

<a id="omega_vision.runtime.catalog.SemanticIdentityCatalog.install_registry"></a>

#### install\_registry

```python
def install_registry(action_tree_store: Any) -> Mapping[str, str]
```

Merge exact exported friendly facts into another level registry.

<a id="omega_vision.runtime.integration"></a>

# omega\_vision.runtime.integration

<a id="omega_vision.runtime.integration.GAME_OBJECT_LEARNER_SCHEMA_VERSION"></a>

#### GAME\_OBJECT\_LEARNER\_SCHEMA\_VERSION

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload"></a>

## GameObjectLearnerPayload Objects

```python
@dataclass(frozen=True)
class GameObjectLearnerPayload()
```

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.state_id"></a>

#### state\_id: `str`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.objects"></a>

#### objects: `tuple[Mapping[str, Any], ...]`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.correspondences"></a>

#### correspondences: `tuple[Mapping[str, Any], ...]`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.transitions"></a>

#### transitions: `tuple[Mapping[str, Any], ...]`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.provenance"></a>

#### provenance: `tuple[str, ...]`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.observation_id"></a>

#### observation\_id: `str | None`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.encounter_ids"></a>

#### encounter\_ids: `tuple[str, ...]`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.identity_ids"></a>

#### identity\_ids: `tuple[str, ...]`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.artifacts"></a>

#### artifacts: `tuple[Mapping[str, Any], ...]`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.evidence"></a>

#### evidence: `tuple[Mapping[str, Any], ...]`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.schema_version"></a>

#### schema\_version: `str`

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.to_dict"></a>

#### to\_dict

```python
def to_dict() -> dict[str, Any]
```

<a id="omega_vision.runtime.integration.GameObjectLearnerPayload.from_dict"></a>

#### from\_dict

```python
@classmethod
def from_dict(cls, value: Mapping[str, Any]) -> "GameObjectLearnerPayload"
```

<a id="omega_vision.runtime.integration.GameObjectLearnerResult"></a>

## GameObjectLearnerResult Objects

```python
@dataclass(frozen=True)
class GameObjectLearnerResult()
```

<a id="omega_vision.runtime.integration.GameObjectLearnerResult.state_id"></a>

#### state\_id: `str`

<a id="omega_vision.runtime.integration.GameObjectLearnerResult.learning_step"></a>

#### learning\_step: `LearningStepResult | None`

<a id="omega_vision.runtime.integration.GameObjectLearnerResult.prediction_id"></a>

#### prediction\_id: `str | None`

<a id="omega_vision.runtime.integration.GameObjectLearnerResult.recommendation"></a>

#### recommendation: `Any`

<a id="omega_vision.runtime.integration.IntegrationError"></a>

## IntegrationError Objects

```python
class IntegrationError(ValueError)
```

<a id="omega_vision.runtime.integration.GameObjectLearnerSchema"></a>

## GameObjectLearnerSchema Objects

```python
class GameObjectLearnerSchema()
```

Small stable contract; providers may add metadata without changing it.

<a id="omega_vision.runtime.integration.GameObjectLearnerSchema.required_object_fields"></a>

#### required\_object\_fields

<a id="omega_vision.runtime.integration.GameObjectLearnerSchema.version"></a>

#### version

<a id="omega_vision.runtime.integration.IntegrationValidator"></a>

## IntegrationValidator Objects

```python
class IntegrationValidator()
```

<a id="omega_vision.runtime.integration.IntegrationValidator.__init__"></a>

#### \_\_init\_\_

```python
def __init__(
        schema: GameObjectLearnerSchema | None = None,
        *,
        registry_identity_ids: set[str] | frozenset[str] | None = None,
        provenance_source_ids: set[str] | frozenset[str] | None = None
) -> None
```

<a id="omega_vision.runtime.integration.IntegrationValidator.validate"></a>

#### validate

```python
def validate(payload: GameObjectLearnerPayload) -> GameObjectLearnerPayload
```

<a id="omega_vision.runtime.integration.Phase2LearnerPayloadBuilder"></a>

## Phase2LearnerPayloadBuilder Objects

```python
class Phase2LearnerPayloadBuilder()
```

Build the frozen learner handoff exclusively from exact Phase 2 records.

<a id="omega_vision.runtime.integration.Phase2LearnerPayloadBuilder.__init__"></a>

#### \_\_init\_\_

```python
def __init__(store: SymbolicStore) -> None
```

<a id="omega_vision.runtime.integration.Phase2LearnerPayloadBuilder.for_observation"></a>

#### for\_observation

```python
def for_observation(observation_id: str) -> GameObjectLearnerPayload
```

<a id="omega_vision.runtime.integration.phase2_transition_analyzer"></a>

#### phase2\_transition\_analyzer

```python
def phase2_transition_analyzer() -> TransitionAnalyzer
```

Analyze one real handoff using the direct Phase 2 change records.

<a id="omega_vision.runtime.integration.phase2_transformation_learner"></a>

#### phase2\_transformation\_learner

```python
def phase2_transformation_learner() -> TransformationLearner
```

Convert direct changes into evidence-linked competing interpretations.

<a id="omega_vision.runtime.integration.phase2_rule_inducer"></a>

#### phase2\_rule\_inducer

```python
def phase2_rule_inducer() -> RuleInducer
```

Induce inspectable rival rules without treating one observation as proof.

<a id="omega_vision.runtime.integration.phase2_rule_ranker"></a>

#### phase2\_rule\_ranker

```python
def phase2_rule_ranker() -> RuleRanker
```

Rank by verified history first, then evidence and explicit simplicity.

<a id="omega_vision.runtime.integration.phase2_rule_executor"></a>

#### phase2\_rule\_executor

```python
def phase2_rule_executor(store: RuleStore,
                         action_or_event: Any) -> RuleExecutor
```

Apply an induced object transformation relative to a new object state.

Numeric ``from``/``to`` observations describe a delta, not an absolute
destination.  This lets a translation learned at one location operate on
an unseen object at another location.  Non-numeric changes use their
observed ``to`` value.  The caller still has to supply the action/event
that selects the rule; execution never silently ignores that condition.

<a id="omega_vision.runtime.integration.GameObjectLearnerPlugin"></a>

## GameObjectLearnerPlugin Objects

```python
class GameObjectLearnerPlugin(ABC)
```

Phase 3 boundary; implementations consume normalized Phase 2 results.

<a id="omega_vision.runtime.integration.GameObjectLearnerPlugin.consume_state"></a>

#### consume\_state

```python
@abstractmethod
def consume_state(payload: GameObjectLearnerPayload) -> NormalizedResult
```

<a id="omega_vision.runtime.integration.GameObjectLearnerPlugin.consume_transition"></a>

#### consume\_transition

```python
@abstractmethod
def consume_transition(before: GameObjectLearnerPayload, action_or_event: Any,
                       after: GameObjectLearnerPayload) -> NormalizedResult
```

<a id="omega_vision.runtime.integration.GameObjectLearnerPlugin.consume"></a>

#### consume

```python
def consume(payload: GameObjectLearnerPayload) -> NormalizedResult
```

Backward-compatible alias for earlier single-state plugins.

<a id="omega_vision.runtime.integration.PipelineGameObjectLearnerPlugin"></a>

## PipelineGameObjectLearnerPlugin Objects

```python
class PipelineGameObjectLearnerPlugin(GameObjectLearnerPlugin)
```

Runnable integration of validated payloads with GameLearningPipeline.

<a id="omega_vision.runtime.integration.PipelineGameObjectLearnerPlugin.__init__"></a>

#### \_\_init\_\_

```python
def __init__(pipeline: GameLearningPipeline,
             *,
             mode: ExecutionMode = ExecutionMode.PYTHON,
             validator: IntegrationValidator | None = None) -> None
```

<a id="omega_vision.runtime.integration.PipelineGameObjectLearnerPlugin.consume_state"></a>

#### consume\_state

```python
def consume_state(payload: GameObjectLearnerPayload) -> NormalizedResult
```

<a id="omega_vision.runtime.integration.PipelineGameObjectLearnerPlugin.consume_transition"></a>

#### consume\_transition

```python
def consume_transition(before: GameObjectLearnerPayload, action_or_event: Any,
                       after: GameObjectLearnerPayload) -> NormalizedResult
```

<a id="omega_vision.runtime.replay"></a>

# omega\_vision.runtime.replay

<a id="omega_vision.runtime.replay.SemanticRecordCodec"></a>

## SemanticRecordCodec Objects

```python
class SemanticRecordCodec()
```

Decode exact JSON artifacts emitted by the semantic capture observer.

<a id="omega_vision.runtime.replay.SemanticRecordCodec.decode"></a>

#### decode

```python
@staticmethod
def decode(record_type: str, value: Mapping[str, Any]) -> Any
```

<a id="omega_vision.runtime.replay.SemanticRecordCodec.decode_namespace"></a>

#### decode\_namespace

```python
@staticmethod
def decode_namespace(namespace: str, value: Mapping[str, Any]) -> Any
```

<a id="omega_vision.runtime.replay.PrologSemanticBackend"></a>

## PrologSemanticBackend Objects

```python
class PrologSemanticBackend()
```

Durable exact-record backend represented as inspectable SWI-Prolog facts.

<a id="omega_vision.runtime.replay.PrologSemanticBackend.FACT"></a>

#### FACT

<a id="omega_vision.runtime.replay.PrologSemanticBackend.__init__"></a>

#### \_\_init\_\_

```python
def __init__(path: Path) -> None
```

<a id="omega_vision.runtime.replay.PrologSemanticBackend.write_once"></a>

#### write\_once

```python
def write_once(namespace: str, record_id: str, value: Any) -> Any
```

<a id="omega_vision.runtime.replay.PrologSemanticBackend.get"></a>

#### get

```python
def get(namespace: str, record_id: str) -> Any | None
```

<a id="omega_vision.runtime.replay.PrologSemanticBackend.values"></a>

#### values

```python
def values(namespace: str) -> tuple[Any, ...]
```

<a id="omega_vision.runtime.replay.AtomSpaceTransport"></a>

## AtomSpaceTransport Objects

```python
class AtomSpaceTransport(Protocol)
```

Transport boundary for a MeTTa/OpenCog AtomSpace implementation.

<a id="omega_vision.runtime.replay.AtomSpaceTransport.query"></a>

#### query

```python
def query(head: str) -> Iterable[str]
```

<a id="omega_vision.runtime.replay.AtomSpaceTransport.assert_expression"></a>

#### assert\_expression

```python
def assert_expression(expression: str) -> None
```

<a id="omega_vision.runtime.replay.MettaFileAtomSpaceTransport"></a>

## MettaFileAtomSpaceTransport Objects

```python
class MettaFileAtomSpaceTransport()
```

Durable AtomSpace transport using an inspectable MeTTa expression file.

The transport deliberately knows nothing about Phase 2 record types. A future
Hyperon, OpenCog, or remote MeTTa transport only needs to provide the same two
operations; ``AtomSpaceSemanticBackend`` retains all identity and codec rules.

<a id="omega_vision.runtime.replay.MettaFileAtomSpaceTransport.HEADER"></a>

#### HEADER

<a id="omega_vision.runtime.replay.MettaFileAtomSpaceTransport.__init__"></a>

#### \_\_init\_\_

```python
def __init__(path: Path) -> None
```

<a id="omega_vision.runtime.replay.MettaFileAtomSpaceTransport.query"></a>

#### query

```python
def query(head: str) -> tuple[str, ...]
```

<a id="omega_vision.runtime.replay.MettaFileAtomSpaceTransport.assert_expression"></a>

#### assert\_expression

```python
def assert_expression(expression: str) -> None
```

<a id="omega_vision.runtime.replay.AtomSpaceSemanticBackend"></a>

## AtomSpaceSemanticBackend Objects

```python
class AtomSpaceSemanticBackend()
```

Exact semantic records stored as queryable ``semantic_record`` Atoms.

<a id="omega_vision.runtime.replay.AtomSpaceSemanticBackend.HEAD"></a>

#### HEAD

<a id="omega_vision.runtime.replay.AtomSpaceSemanticBackend.__init__"></a>

#### \_\_init\_\_

```python
def __init__(transport: AtomSpaceTransport | None = None,
             *,
             path: Path | None = None) -> None
```

<a id="omega_vision.runtime.replay.AtomSpaceSemanticBackend.write_once"></a>

#### write\_once

```python
def write_once(namespace: str, record_id: str, value: Any) -> Any
```

<a id="omega_vision.runtime.replay.AtomSpaceSemanticBackend.get"></a>

#### get

```python
def get(namespace: str, record_id: str) -> Any | None
```

<a id="omega_vision.runtime.replay.AtomSpaceSemanticBackend.values"></a>

#### values

```python
def values(namespace: str) -> tuple[Any, ...]
```

<a id="omega_vision.runtime.replay.ActionTreeSemanticReplay"></a>

## ActionTreeSemanticReplay Objects

```python
class ActionTreeSemanticReplay()
```

Rebuild a semantic store from the exact records linked by an action tree.

<a id="omega_vision.runtime.replay.ActionTreeSemanticReplay.ORDER"></a>

#### ORDER

<a id="omega_vision.runtime.replay.ActionTreeSemanticReplay.replay"></a>

#### replay

```python
def replay(action_tree_root: Path, store: SymbolicStore) -> SymbolicStore
```

<a id="omega_vision.runtime.transcript"></a>

# omega\_vision.runtime.transcript

<a id="omega_vision.runtime.transcript.TranscriptComparison"></a>

## TranscriptComparison Objects

```python
@dataclass(frozen=True)
class TranscriptComparison()
```

<a id="omega_vision.runtime.transcript.TranscriptComparison.expected_events"></a>

#### expected\_events: `int`

<a id="omega_vision.runtime.transcript.TranscriptComparison.actual_events"></a>

#### actual\_events: `int`

<a id="omega_vision.runtime.transcript.TranscriptComparison.exact_matches"></a>

#### exact\_matches: `int`

<a id="omega_vision.runtime.transcript.TranscriptComparison.ordered_prefix_matches"></a>

#### ordered\_prefix\_matches: `int`

<a id="omega_vision.runtime.transcript.TranscriptComparison.event_recall"></a>

#### event\_recall: `float`

<a id="omega_vision.runtime.transcript.TranscriptComparison.exact"></a>

#### exact: `bool`

<a id="omega_vision.runtime.transcript.TranscriptScorer"></a>

## TranscriptScorer Objects

```python
class TranscriptScorer()
```

Compare structured transcripts without confusing order with membership.

<a id="omega_vision.runtime.transcript.TranscriptScorer.compare"></a>

#### compare

```python
def compare(expected: Iterable[Any],
            actual: Iterable[Any]) -> TranscriptComparison
```
