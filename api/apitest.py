
def api_test(session,request):
    data = request.json
    smsg = session["username"]
    smsg += "api_test message"

    print("DEBUG: INSIDE THE API_TEST ROUTINE")
    print("JSON DATA RETRIEVED",data["var1"])
    
    return {"msg":"api_test message this is from the server."}