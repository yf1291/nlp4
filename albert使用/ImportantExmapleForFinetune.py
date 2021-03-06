from transformers import BartTokenizer, BartForQuestionAnswering, AdamW
import torch # 试着在这个上面做finetune
# 可以手动去https://huggingface.co/valhalla/bart-large-finetuned-squadv1#   下载需要的文件.
tokenizer = BartTokenizer.from_pretrained('/mnt/qa_data')  # 只是一个纯英文的字典.
model = BartForQuestionAnswering.from_pretrained('/mnt/qa_data')

question, text = "Who am I ?", "he a nice dog in China, I am Zhangbo, and i love it very much, i deadly wanna to eat it"
#---------Notes!!!!!!!!!
'''
上面这个问题的答案显然是Zhangbo,但是我就骗骗要把他finetune成a nice dog. 下面我们来进行finetune.
'''
encoding = tokenizer(question, text, return_tensors='pt')
input_ids = encoding['input_ids']
attention_mask = encoding['attention_mask']
class A():
    pass
args=A()
args.learning_rate=3e-5
args.adam_epsilon=1e-8
args.weight_decay=0
no_decay = ["bias", "LayerNorm.weight"]
optimizer_grouped_parameters = [
    {
        "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
        "weight_decay": args.weight_decay,
    },
    {"params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)], "weight_decay": 0.0},
]
optimizer = AdamW(optimizer_grouped_parameters, lr=args.learning_rate, eps=args.adam_epsilon)
#开启finetune模式 ,,,,,,,C:\Users\Administrator\.PyCharm2019.3\system\remote_sources\-456540730\-337502517\transformers\data\processors\squad.py 从这个里面进行抄代码即可.
model.zero_grad()
model.train()


for _ in range(100):
    batch=[input_ids,attention_mask,torch.tensor([0]),torch.tensor([3])]
    inputs = {
        "input_ids": batch[0],
        "attention_mask": batch[1],

        "start_positions": batch[2],
        "end_positions": batch[3],
    }
    print('start_train')
    outputs = model(**inputs)
    loss = outputs[0]
    print(loss)
    loss.backward()
    optimizer.step()

    model.zero_grad()


print("train_over!!!!!!!!!!")

#---------下面开始测试
model.eval()
start_scores, end_scores = model(input_ids, attention_mask=attention_mask, output_attentions=False)[:2]




all_tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
answer = ' '.join(all_tokens[torch.argmax(start_scores) : torch.argmax(end_scores)+1])
answer = tokenizer.convert_tokens_to_ids(answer.split())
answer = tokenizer.decode(answer)






print(answer)
#answer => 'a nice puppet'