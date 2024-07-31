import toolbox.tools.aggregation.result as tool

#
# tool.event_location()

# GET EVENTS
# output=tool.entertainment_data("上海")
# with open('./output/tools_test_output.txt','w',encoding='utf-8') as f:
#     f.write(str(output))
# print(len(output.get('sight',[])))
# print(len(output.get('food',[])))
# print(len(output.get('hotel',[])))

# GET ROUTE GO BACK
# res=tool.travel_data('北京','上海')
# print(res)







output=tool.event_route(events = [
        {
            "city": "北京",
            "address": "北京市延庆区G6京藏高速58号出口"
        },
        {
            "city": "北京",
            "address": "北京市西城区前海西街17号"
        }
    ]
)
# output=tool.event_route(events = [
#         {
#             "city": "北京",
#             "address": "辰安科技公司"
#         },
#         {
#             "city": "北京",
#             "address": "北京市西城区前海西街17号"
#         }
#     ]
# )
print(output)