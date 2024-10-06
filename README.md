# Jira: 유저 Slack Id 싱크

## 목적
1. 내 Slack workspace에 있는 모든 유저의 이메일 정보와 Jira workspace의 이메일 정보를 비교하여 Jira의 metadata에 slack id를 추가한다.
2. 추가된 slack id를 가지고 Jira Automation을 이용하여 슬랙에 커스터마이징된 알람을 보내는 기능에 사용한다.

## 사용 방법
1. config.ini를 생성하여 다음 값을 정의한다.
    1. *SLACK_TOKEN*: 내 슬랙 Workspace에 연동된 slack app의 token 값 (slack app 연동을 위해선 회사 어드민 허가가 필요할 수 있다. 그리고 slack app에 유저 정보를 조회할 수 있는 권한이 필요하다.)
    2. *JIRA_URL*: 내 회사의 jira 도메인을 입력한다.
    3. *USERNAME*: JIRA API Key를 지급받은 내 회사 이메일
    4. *APIKEY*: 내 JIRA API Key
    5. config.ini 파일 예시
        ``` ini
        [DEFAULT]
        SLACK_TOKEN = xoxb-XXXXYYYYZZZZ
        JIRA_URL = https://mycompany.atlassian.net/
        USERNAME = james.kang@mycompany.com
        APIKEY = AAAABBBBCCCCDDDD
        ```
2. python3를 설치한 후 "python3 main.py" 명령어를 콘솔에 입력하면 싱크 작업이 실행된다.
3. 작업이 마무리된 다음 jira에서 assignee.properties.metadata.slack_id에 잘 반영 됐는지 확인한다.

## 코드 설명
1. main.py: slack_api와 jira_api에 등록된 코드를 호출하여 싱크 작업을 실행한다.
2. slack_api.py: Slack에서 active 유저 정보를 불러오도록 한다.
3. jira_api.py: Jira Object를 생성하고 해당 object를 사용할 수 있도록 한다.
