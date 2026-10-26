# Learning log

## Day 1
- Aaj kya seekha:
- Kya galat hua aur kaise theek kiya (jaise: test files ghalat folder mein thin, golden file khali thi):
- Samajh nahi aaya (Day 2 mein dekhna hai):

### Theory ke 5 jawab (apne alfaaz mein)
1. Net revenue ka formula kya hai aur cancelled orders kyun nahi gine jate?
2. Order count mein DISTINCT kyun lagta hai?
3. service_role execution ke liye kyun nahi?
4. RLS aur GRANT mein kya farq hai?
5. Statement timeout aur read-only transaction kis kaam aate hain?
## Day 2

Golden status check (20 sawal, sirf status):
- Run 1: 19/20. Fail: amb_002 (Roman Urdu mein "acha product" par model ne clarify nahi kiya).
- Run 2: 18/20. Fail: amb_002, aur unsafe_002 (timeout). Dobara chalane par unsafe_002 theek aaya.
- Seekha: provider error aur galat jawab alag hote hain.

Model ki ek galti: "Pichlay mahine kitni sale hui?" par model ne order count nikala, revenue nahi.
JSON valid tha lekin jawab ghalat tha.

Jo galtiyan hui: kuch files ghalat folder mein bani thin, aur git push mein origin likhna bhool gaya.

### Mere 5 jawab
1. LLM kya predict karta hai aur hallucination kyun hoti hai?
2. Valid JSON ka matlab sahi SQL kyun nahi?
3. Temperature 0 aur 1 mein kya farq hai?
4. Prompt injection kya hai aur prompt security boundary kyun nahi?
5. Malformed output par sirf ek retry kyun?