import FDDC_PART2.expand.NER_IDCNN_CRF.main as main

model, sess, char_to_id, id_to_tag = main.evaluate_line2()
line = '中天科技是国内最早开发海底线缆产品的制造商，通过不断加大科研投入和自主技术创新，拥有多项海缆制造的核心技术，多年来，保持国内市场占有率第 一， 为国内第一个出口欧美的海底线缆制造商。为充分发挥公司海洋系列产品的优势，公司进一步延伸海底线缆业务板块，目前已形成海底光缆、海底电缆、接驳盒、水下连接器件等海洋系列产业链，并向海缆总包业务方向拓展，率先实现从海底线缆供应商向海缆项目整体解决方案系统集成商的转型。'
result = model.evaluate_line(sess, main.input_from_line(line, char_to_id), id_to_tag)

print(result)
