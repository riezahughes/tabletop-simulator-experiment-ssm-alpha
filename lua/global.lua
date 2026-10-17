-- Alert spinner. Disc: 4 sectors on the right half, 45 deg each, clockwise from top:
-- Patrol, Wary, Lockdown, Combat. Left half is the logo: no sector, spin again.
local SECTORS = {"PATROL", "WARY", "LOCKDOWN", "COMBAT"}
local spinning = false

function onLoad()
  if SNAPS then Global.setSnapPoints(SNAPS) end
  local disc = getObjectFromGUID("d15c01")
  disc.createButton({click_function = "spin", function_owner = Global, label = "SPIN",
    position = {0, 0.2, 1.7}, width = 700, height = 300, font_size = 200, tooltip = "Spin the Alert disc"})
end

function spin()
  if spinning then return end
  spinning = true
  startLuaCoroutine(Global, "spinRoutine")
end

function spinRoutine()
  local n = getObjectFromGUID("ae3d01")
  local v = 12 + math.random() * 10
  local a = n.getRotation().y
  while v > 0.15 do
    a = (a + v) % 360
    n.setRotation({0, a, 0})
    v = v * 0.985
    coroutine.yield(0)
  end
  spinning = false
  local res = SECTORS[math.floor(((a - 180) % 360) / 45) + 1]
  broadcastToAll(res and ("ALERT: " .. res) or "Logo side: no result, spin again", {1, 1, 0})
  return 1
end

