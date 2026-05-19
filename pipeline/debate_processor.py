import Helper.agent_loop_tools as tl
from Helper.checkpoint_manager import check_existing_answer
from Helper.checkpoint_manager import update_checkpoint
# ================================================
#  MAIN ORCHESTRATOR — CLEAN VERSION
# ================================================
def run_agentic_rag(domains, evidences, question, cp, max_rounds=3):

    tl.ensure_debate_storage(cp)
    critic_mem = cp["debate"].get("critic", "")

    for r in range(1,max_rounds + 1):
        print(f"\n========= ROUND {r} =========")

        # Domain agents
        outputs = []
        for d, ev in zip(domains, evidences):
            try:
                domain_memory = tl.collect_domain_arguments(cp, r, d)
                out = tl.domain_agent_cached(d, question, ev, domain_memory, critic_mem, cp, r)
            except:
                out =None
                update_checkpoint(question, cp)
            outputs.append({"domain": d, "response": out or "ERROR"})

        try:
            summary = tl.moderator_cached(outputs, question, cp, r)
        except:
            summary = 'error'
            update_checkpoint(question, cp)
        try:
            prev_round = str(r - 1)
            if prev_round in cp.get("debate", {}):
                previous_critiques = cp["debate"][prev_round].get("critic", [])
            else:
                previous_critiques = ''

            verdict = tl.critic_cached(summary,evidences,previous_critiques,question, cp, r)
        except:
            verdict = 'error'
            update_checkpoint(question, cp)

        critic_mem = verdict
        # ACCEPT → final
        if verdict.strip().upper().startswith("ACCEPT"):
            print("\n🎉 ACCEPT — generating final theory + experiment...")

            theory = tl.final_theory_cached(summary, question, cp, r)
            sugg   = tl.experiment_cached(theory, question, cp, r)
            return sugg

    # Max rounds hit
    print("\n⚠️ Max rounds reached: no accept, use last round result to generate theory and experiment")
    try:
        theory = tl.final_theory_cached(summary, question, cp, r)
    except:
        theory ='error'
        update_checkpoint(question, cp)
    try:
        sugg   = tl.experiment_cached(theory, question, cp, r)
    except:
        sugg = 'error'
        update_checkpoint(question, cp)
    return sugg


from pipeline.question_processor import process_question
from pipeline.rag_processor import initial_process_rag

def run_single_debate(question,rag_n=3 ,max_debate_rounds=10):

    checkpoint = process_question(question) 
    output_expert, output_rag = initial_process_rag(checkpoint, rag_n)##
    final_answer= run_agentic_rag(output_expert,output_rag,question,checkpoint, max_rounds=max_debate_rounds)
    
    return final_answer



