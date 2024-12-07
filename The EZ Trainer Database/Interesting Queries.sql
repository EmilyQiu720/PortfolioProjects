use ieor215_project;
-- Interesting queries:

-- Query 1:
WITH Client_BMI_Change AS (
    SELECT 
        M.Member_ID,
        MCN.Employee_ID AS Nutritionist_ID,
        (MAX(M.BMI) - MIN(M.BMI)) AS BMI_Change
    FROM 
        Member M
    JOIN 
        Member_Consults_Nutritionist MCN
    ON 
        M.Member_ID = MCN.Member_ID
    WHERE 
        M.Membership_status = 'Active'
    GROUP BY 
        M.Member_ID, MCN.Employee_ID
),
Nutritionist_Performance AS (
    SELECT 
        Nutritionist_ID,
        SUM(BMI_Change) AS Total_BMI_Change,
        COUNT(Member_ID) AS Active_Client_Count
    FROM 
        Client_BMI_Change
    GROUP BY 
        Nutritionist_ID
),


Top_Nutritionists AS (
    SELECT 
        NP.Nutritionist_ID,
        E.Pay_rate,
        NP.Total_BMI_Change,
        NP.Active_Client_Count
    FROM 
        Nutritionist_Performance NP
    JOIN 
        Employee E
    ON 
        NP.Nutritionist_ID = E.Employee_ID
    ORDER BY 
        NP.Total_BMI_Change DESC
)

SELECT 
    TN.Nutritionist_ID,
    TN.Pay_rate,
    TN.Active_Client_Count
FROM 
    Top_Nutritionists TN;

-- Query 2
SELECT 
    VE.Type AS Equipment_Type, 
    VE.Name AS Equipment_Name, 
    COUNT(WSE.Equipment_ID) AS Usage_Count
FROM 
    Workout_Session_Uses_Equipment WSE
JOIN 
    VR_Equipment VE
ON 
    WSE.Equipment_ID = VE.Equipment_ID
GROUP BY 
    VE.Type, VE.Name
ORDER BY 
    Usage_Count DESC;

-- Query 3
SELECT 
    M.Member_ID,
    AVG(M.BMI) AS Average_BMI,
    COUNT(WS.Workout_ID) AS Workout_Session_Count,
    AVG(M.BMI) / NULLIF(COUNT(WS.Workout_ID), 0) AS BMI_Per_Workout_Session
FROM 
    Member M
LEFT JOIN 
    Member_Participates_Workout_Session MPWS
ON 
    M.Member_ID = MPWS.Member_ID
LEFT JOIN 
    Workout_Session WS
ON 
    MPWS.Workout_ID = WS.Workout_ID
WHERE 
    M.Membership_status = 'Active'
GROUP BY 
    M.Member_ID
ORDER BY 
    Average_BMI DESC;