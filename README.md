# 课设接口

**URL:** .....

## 上传数据
**path：** /  
**methods：** POST  
**request params：** 


Name | Type | Discription
---|--- | ---
sid | String |设备id
T |  Double | 体温
hb | Double | 心跳
bo | Double | 血氧


**response：** 200 OK

## 查询一天数据
**path：** /*sid*/*days*  
**methods：** GET  
**request params：** 


Name | Type | Discription
---|--- | ---
sid | String |设备id
days| Integer| 查询天数（单位：天）



**response type：** JSON   
**response datas：**


Name | Type | Discription
---|--- | ---
id | Integer | 数据库id
sid | String | 设备id
T | Double | 体温
hb | Integer | 心跳
bo | Integer | 血氧
ctime | String | 上传时间，原为 Timestamp 格式


## 数据分析
**path：** /analyze/*sid*  
**methods：** GET  
**request params：** 


Name | Type | Discription
---|--- | ---
sid | String |设备id



**response type：** JSON   
**response datas：**
```
{
    "temporate_diff" : Double 最大体温差,
    "fever_zone": 发热区间 
        [
            [String  开始时间, String 结束时间] 
            .....
        ],
    "low_temporate_zone": 低温区间
        [
            [String  开始时间, String 结束时间] 
            .....
        ],
    
    "low_bo": Integer 最低血氧值,
    "low_bo_zone": 低血氧区间
        [
            [String  开始时间, String 结束时间] 
            .....
        ],
    
    "high_hb": Integer 最高心跳数,
    "low_hb": Integer 最低心跳数,
    "high_hb_zone": 高心跳区间
        [
            [String  开始时间, String 结束时间] 
            .....
        ],
    "low_hb_zone": 低心跳区间
        [
            [String  开始时间, String 结束时间] 
            .....
        ],
    
    "req_state": Integer 请求参数
}
```
其中：  
- req_state：200 时正常，404 表示没有该用户
- 每个区间的时间格式为 String： "12:34"
