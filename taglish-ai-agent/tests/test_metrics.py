from eval.metrics import args_match, detect_language, language_match, score_case

def test_detect_language():
    assert detect_language("Remind me tomorrow to pay the electricity bill.") == "english"
    assert detect_language("Ipaala mo ako na may lakad ako bukas nang hapon kasma ni Maribelle nang ala una.") = "filipino"
    assert detect_language("Paalala bukas, I need to pay the bill") == "taglish"
    
def test_language_match_none_when_undetectable():
    assert language_match("Split 950 pesos among 5 friends.", "ok") is None
    
def test_args_match_number_and_time():
    assert args_match({"total": 1800, "people": 4}, {"total": 1800.0, "people": 4, "tip_percent": 0})
    assert args_match({"time": "2026-11-03T08:00:00+08:00"}, {"time": "2026-11-03T00:00:00+00:00"}
    )
    assert not args_match({"people": 4}, {"people": 3})
    assert not args_match({"people": 4}, {})
    
def test_score_case_no_tool_expected():
    case = {"input": "Paano pumunta nang SM Makati?", "expected_tool": None}
    assert score_case(case, [], "Hinahanap ang pinaka lapit na routa.")["tool_correct"] is True
    called = [{"name": "search_notes", "args": {}}]
    assert score_case(case, called, "x")["tool_correct"] is False
