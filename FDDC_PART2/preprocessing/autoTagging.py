import FDDC_PART2.preprocessing.htmlParser as parser

# 20315972
# 宁夏汉尧石墨烯储能材料科技有限公司	湖南百利工程科技股份有限公司
# 锂离子电池石墨烯三元正极材料及导电浆料
# 锂离子电池石墨烯三元正极材料及导电浆料项目智能产线设计建造合同
# 1295000000
# 1295000000
# 北京高能时代环境技术股份有限公司

trainline = '20315972	宁夏汉尧石墨烯储能材料科技有限公司	湖南百利工程科技股份有限公司	锂离子电池石墨烯三元正极材料及导电浆料	锂离子电池石墨烯三元正极材料及导电浆料项目智能产线设计建造合同	1295000000	1295000000	北京高能时代环境技术股份有限公司'


def tag_text(htmlpath, trainline):
    s_arr = parser.levelText(htmlpath)
    for s in s_arr:
        print(s)


tag_text('/home/utopia/corpus/FDDC_part2_data/round1_train_20180518/重大合同/html/20315972.html', '')
