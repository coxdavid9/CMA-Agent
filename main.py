import asyncio
from cma_agent.agent import ask
async def main():
    print("CMA Study Agent — type quit to exit")
    while True:
        x=input("\nYou: ").strip()
        if x.lower()=="quit": break
        print("\nAgent:",await ask(x))
if __name__=="__main__": asyncio.run(main())
