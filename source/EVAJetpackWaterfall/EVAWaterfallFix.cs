using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

namespace GreenstoneIndustry.EVAWaterfallFix
{
    /// <summary>
    /// Exposes the KerbalEVA jetpack thrust vector as six scalar float fields so that
    /// Waterfall's CustomPullController can read them (it cannot read Vector3 members).
    /// Fields: xPos/xNeg, yPos/yNeg, zPos/zNeg  (each >= 0, in the kerbal's local frame)
    /// </summary>
    public class EVAPackInput : PartModule
    {
        public float xNeg;
        public float xPos;
        public float yNeg;
        public float yPos;
        public float zNeg;
        public float zPos;

        PartModule evaModule;
        FieldInfo packLinearField;
        PropertyInfo fuelProp;

        public override void OnStart(StartState state)
        {
            base.OnStart(state);
            FindEva();
        }

        void FindEva()
        {
            try
            {
                PartModuleList mods = part.Modules;
                if (mods == null) return;
                for (int i = 0; i < mods.Count; i++)
                {
                    PartModule m = mods[i];
                    if (m == null) continue;
                    if (m.GetType().Name == "KerbalEVA")
                    {
                        evaModule = m;
                        Type t = m.GetType();
                        BindingFlags f = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
                        packLinearField = t.GetField("packLinear", f);
                        fuelProp = t.GetProperty("Fuel", f);
                        return;
                    }
                }
            }
            catch (Exception) { }
        }

        void LateUpdate()
        {
            if (evaModule == null)
            {
                FindEva();
                if (evaModule == null) return;
            }

            // KerbalEVA.packLinear is the *commanded* thrust: it is assigned before the fuel
            // check (KerbalEVA.cs L12337) and therefore stays non-zero after the tank runs dry -
            // KSP just returns and skips AddForce (L12349). Reading it alone leaves the plume
            // burning on an empty pack, so gate on Fuel, the very value KSP tests itself.
            if (fuelProp != null)
            {
                double fuel;
                try { fuel = Convert.ToDouble(fuelProp.GetValue(evaModule, null)); }
                catch (Exception) { fuel = 1.0; }
                if (fuel <= 0.0)
                {
                    xPos = 0f; xNeg = 0f;
                    yPos = 0f; yNeg = 0f;
                    zPos = 0f; zNeg = 0f;
                    return;
                }
            }

            if (packLinearField == null) return;

            Vector3 v;
            try { v = (Vector3)packLinearField.GetValue(evaModule); }
            catch (Exception) { return; }

            Vector3 local;
            try { local = Quaternion.Inverse(part.transform.rotation) * v; }
            catch (Exception) { return; }

            xPos = Mathf.Max(0f, local.x);
            xNeg = Mathf.Max(0f, -local.x);
            yPos = Mathf.Max(0f, local.y);
            yNeg = Mathf.Max(0f, -local.y);
            zPos = Mathf.Max(0f, local.z);
            zNeg = Mathf.Max(0f, -local.z);
        }
    }

    /// <summary>
    /// KSP's built-in kerbal EVA cannot host Waterfall effects out of the box:
    ///  1. Part.FindModelTransforms() starts at transform.Find("model"), and the EVA model
    ///     hierarchy is not reachable from there, so Waterfall never resolves an anchor.
    ///  2. ModuleWaterfallFX runs its one-shot Initialize() before the EVA model is assembled.
    ///
    /// The jetpack model already ships 18 stock gas-jet emitters named
    ///   fx_gasJet_&lt;pos&gt;_&lt;axis&gt;&lt;sign&gt;      e.g. fx_gasJet_l_y+
    /// The trailing tag says which way that emitter pushes (x+/x-/y+/y-/z+/z-) and each emitter
    /// transform carries a real local position inside the pack. This addon creates an empty
    /// "model" container plus one dummy transform per direction slot, parks it on the matching
    /// emitter, and aims the plume along the exhaust axis (exhaust = opposite of the commanded
    /// thrust, so the plume stays axis aligned exactly like a normal RCS nozzle).
    ///
    /// The stock fx_gasJet particles are silenced once the Waterfall effects are actually there.
    /// </summary>
    [KSPAddon(KSPAddon.Startup.Flight, false)]
    public class EVAWaterfallFixer : MonoBehaviour
    {
        static readonly BindingFlags PROT = BindingFlags.NonPublic | BindingFlags.Instance;
        const string EMITTER_PREFIX = "fx_gasJet";

        class Probe
        {
            public bool suppressed;
            public bool initialized;
            public Transform modelRoot;
            public Transform root;
            public readonly List<Transform> slots = new List<Transform>();
            public readonly Dictionary<string, Transform> dummies = new Dictionary<string, Transform>();
            public readonly Dictionary<string, List<Transform>> groups = new Dictionary<string, List<Transform>>();
            public readonly Dictionary<string, Transform> slotEmitter = new Dictionary<string, Transform>();
            public int emitterCount;
            public bool defaultsDone;
        }

        // Slot names are what the part config points at. They encode the DIRECTION the slot
        // serves (XPos = thrust +X, YNeg = thrust -Y, ...). The trailing digit is the index
        // inside that direction group; the emitter names supply the rest.
        static readonly string[] SLOT_NAMES =
        {
            "EVAJetXNeg1", "EVAJetXNeg2",
            "EVAJetXPos1", "EVAJetXPos2",
            "EVAJetYNeg1", "EVAJetYNeg2",
            "EVAJetYPos1", "EVAJetYPos2", "EVAJetYPos3", "EVAJetYPos4",
            "EVAJetZNeg1", "EVAJetZNeg2", "EVAJetZNeg3", "EVAJetZNeg4",
            "EVAJetZPos1", "EVAJetZPos2", "EVAJetZPos3", "EVAJetZPos4"
        };

        /// <summary>exhaust direction for a slot (opposite of the commanded thrust)</summary>
        static Vector3 SlotAxis(string slot)
        {
            if (slot.StartsWith("EVAJetXPos", StringComparison.Ordinal)) return new Vector3(-1f, 0f, 0f);
            if (slot.StartsWith("EVAJetXNeg", StringComparison.Ordinal)) return new Vector3(1f, 0f, 0f);
            if (slot.StartsWith("EVAJetYPos", StringComparison.Ordinal)) return new Vector3(0f, -1f, 0f);
            if (slot.StartsWith("EVAJetYNeg", StringComparison.Ordinal)) return new Vector3(0f, 1f, 0f);
            if (slot.StartsWith("EVAJetZPos", StringComparison.Ordinal)) return new Vector3(0f, 0f, -1f);
            if (slot.StartsWith("EVAJetZNeg", StringComparison.Ordinal)) return new Vector3(0f, 0f, 1f);
            return Vector3.up;
        }

        /// <summary>the emitter-name suffix that feeds a slot, e.g. "y+"</summary>
        static string SlotGroup(string slot)
        {
            if (slot.StartsWith("EVAJetXPos", StringComparison.Ordinal)) return "x+";
            if (slot.StartsWith("EVAJetXNeg", StringComparison.Ordinal)) return "x-";
            if (slot.StartsWith("EVAJetYPos", StringComparison.Ordinal)) return "y+";
            if (slot.StartsWith("EVAJetYNeg", StringComparison.Ordinal)) return "y-";
            if (slot.StartsWith("EVAJetZPos", StringComparison.Ordinal)) return "z+";
            if (slot.StartsWith("EVAJetZNeg", StringComparison.Ordinal)) return "z-";
            return "";
        }

        /// <summary>trailing digits of a slot name, minus one</summary>
        static int SlotIndex(string slot)
        {
            int i = slot.Length - 1;
            while (i >= 0 && char.IsDigit(slot[i])) i--;
            int v;
            if (int.TryParse(slot.Substring(i + 1), out v)) return v - 1;
            return 0;
        }

        /// <summary>suffix of an emitter object name: fx_gasJet_l_y+ -> "y+"</summary>
        static string EmitterGroup(string nm)
        {
            int us = nm.LastIndexOf('_');
            if (us < 0 || us + 1 >= nm.Length) return "";
            return nm.Substring(us + 1);
        }

        readonly Dictionary<int, Probe> probes = new Dictionary<int, Probe>();

        void Start() { StartCoroutine(Watch()); }

        IEnumerator Watch()
        {
            WaitForSeconds wait = new WaitForSeconds(0.5f);
            while (true)
            {
                yield return wait;
                try { Scan(); }
                catch (Exception e) { Debug.LogError("[EVAWaterfallFix] " + e); }
            }
        }

        void LateUpdate()
        {
            foreach (KeyValuePair<int, Probe> kv in probes)
            {
                Probe pr = kv.Value;
                if (pr.root == null) continue;
                SyncDummies(pr);
            }
        }

        void Scan()
        {
            if (FlightGlobals.Vessels == null) return;
            for (int vi = 0; vi < FlightGlobals.Vessels.Count; vi++)
            {
                Vessel v = FlightGlobals.Vessels[vi];
                if (v == null || v.parts == null) continue;
                for (int pi = 0; pi < v.parts.Count; pi++)
                {
                    Part p = v.parts[pi];
                    if (p == null || p.name == null) continue;
                    if (p.name.IndexOf("kerbalEVA", StringComparison.Ordinal) != 0) continue;
                    Handle(p);
                }
            }
        }

        void Handle(Part p)
        {
            int id = p.GetInstanceID();
            Probe pr;
            if (!probes.TryGetValue(id, out pr))
            {
                pr = new Probe();
                probes[id] = pr;
            }
            if (pr.root == null) pr.root = p.transform;
            if (pr.modelRoot == null) pr.modelRoot = p.transform.Find("model");

            if (pr.emitterCount == 0) CaptureEmitters(p, pr);
            if (pr.emitterCount == 0) return;

            if (!pr.initialized)
            {
                EnsureSlotDummies(p, pr);

                List<PartModule> wfs = FindWaterfallModules(p);
                MethodInfo mi = null;
                int ok = 0;
                for (int wi = 0; wi < wfs.Count; wi++)
                {
                    PartModule wf = wfs[wi];
                    if (mi == null) mi = wf.GetType().GetMethod("Initialize", PROT);
                    if (mi == null)
                    {
                        Debug.LogError("[EVAWaterfallFix] no protected Initialize() on " + wf.GetType().FullName);
                        break;
                    }
                    try { mi.Invoke(wf, null); ok++; }
                    catch (Exception e) { Debug.LogError("[EVAWaterfallFix] Initialize threw: " + e.InnerException); }
                }
                pr.initialized = true;
                Debug.Log("[EVAWaterfallFix] re-initialized " + ok + "/" + wfs.Count + " WaterfallFX module(s) on " + p.name);

                // The Waterfall in-game editor snapshots FlightGlobals.ActiveVessel once, 5 frames
                // after the flight scene loads - i.e. long before the kerbal goes EVA - and never
                // refreshes. Nudge it so the EVA modules show up in the parts list.
                StartCoroutine(RefreshWaterfallUI(2f));
            }

            // Only silence the stock jet particles once the Waterfall effects are actually there.
            // If detection or the template ever fails, the kerbal keeps the original plume
            // rather than ending up with no jet visual at all.
            if (!pr.suppressed)
            {
                if (ActiveFxTotal(p) > 0)
                {
                    int n = SuppressGasJets(p);
                    if (n > 0)
                    {
                        pr.suppressed = true;
                        Debug.Log("[EVAWaterfallFix] suppressed " + n + " fx_gasJet on " + p.name);
                    }
                }
            }
        }

        IEnumerator RefreshWaterfallUI(float delay)
        {
            yield return new WaitForSeconds(delay);
            try
            {
                Type ui = null;
                Assembly[] asms = AppDomain.CurrentDomain.GetAssemblies();
                for (int i = 0; i < asms.Length; i++)
                {
                    try { ui = asms[i].GetType("Waterfall.UI.WaterfallUI", false); }
                    catch (Exception) { ui = null; }
                    if (ui != null) break;
                }
                if (ui == null) yield break;

                PropertyInfo instProp = ui.GetProperty("Instance", BindingFlags.Public | BindingFlags.Static);
                object inst = instProp != null ? instProp.GetValue(null, null) : null;
                if (inst == null) yield break;

                MethodInfo mi = ui.GetMethod("GetVesselData", BindingFlags.Public | BindingFlags.Instance);
                if (mi == null) yield break;

                mi.Invoke(inst, null);
            }
            catch (Exception e)
            {
                Debug.LogError("[EVAWaterfallFix][ui] " + e);
            }
        }

        // ---------------- placement ----------------

        static void CaptureEmitters(Part p, Probe pr)
        {
            Transform[] all = p.GetComponentsInChildren<Transform>(true);
            for (int i = 0; i < all.Length; i++)
            {
                Transform t = all[i];
                if (t == null || t.gameObject == null) continue;
                string nm = t.gameObject.name;
                if (nm.IndexOf(EMITTER_PREFIX, StringComparison.Ordinal) != 0) continue;
                string g = EmitterGroup(nm);
                if (g.Length == 0) continue;
                List<Transform> l;
                if (!pr.groups.TryGetValue(g, out l))
                {
                    l = new List<Transform>();
                    pr.groups[g] = l;
                }
                bool dup = false;
                for (int k = 0; k < l.Count; k++) { if (l[k] == t) { dup = true; break; } }
                if (!dup) { l.Add(t); pr.emitterCount++; }
            }

            // keep a stable order so slot indices stay put between sessions
            foreach (KeyValuePair<string, List<Transform>> kv in pr.groups)
            {
                kv.Value.Sort(delegate (Transform a, Transform b)
                {
                    if (a == null) return 1;
                    if (b == null) return -1;
                    return string.CompareOrdinal(a.gameObject.name, b.gameObject.name);
                });
            }
        }

        void EnsureSlotDummies(Part p, Probe pr)
        {
            if (pr.modelRoot == null)
            {
                Transform existing = p.transform.Find("model");
                if (existing != null) pr.modelRoot = existing;
                else
                {
                    GameObject g = new GameObject("model");
                    g.transform.SetParent(p.transform, false);
                    pr.modelRoot = g.transform;
                }
            }

            for (int i = 0; i < SLOT_NAMES.Length; i++)
            {
                string nm = SLOT_NAMES[i];
                if (pr.dummies.ContainsKey(nm)) continue;
                GameObject g = new GameObject(nm);
                g.transform.SetParent(pr.modelRoot, false);
                pr.dummies[nm] = g.transform;
                pr.slots.Add(g.transform);
            }

            if (!pr.defaultsDone)
            {
                pr.defaultsDone = true;
                AssignEmitters(pr);
            }
            SyncDummies(pr);
        }

        /// <summary>
        /// Each slot takes the next emitter carrying the matching tag
        /// (x+ slots take the fx_gasJet_*_x+ emitters, in name order).
        /// </summary>
        static void AssignEmitters(Probe pr)
        {
            for (int i = 0; i < SLOT_NAMES.Length; i++)
            {
                string slot = SLOT_NAMES[i];
                string group = SlotGroup(slot);
                List<Transform> list;
                if (!pr.groups.TryGetValue(group, out list) || list.Count == 0) continue;
                int idx = SlotIndex(slot);
                if (idx >= list.Count) idx = idx % list.Count;
                pr.slotEmitter[slot] = list[idx];
            }
        }

        static void SyncDummies(Probe pr)
        {
            Transform root = pr.root;
            if (root == null) return;
            Transform space = pr.modelRoot != null ? pr.modelRoot : root;

            for (int i = 0; i < pr.slots.Count; i++)
            {
                Transform d = pr.slots[i];
                if (d == null) continue;

                string slot = d.gameObject.name;

                Transform use;
                if (!pr.slotEmitter.TryGetValue(slot, out use) || use == null)
                {
                    d.gameObject.SetActive(false);
                    continue;
                }

                // After the effects exist, follow the emitter's own visibility: when the kerbal
                // stows the pack the plume must disappear with it. Before initialization the
                // dummy must stay active, because Waterfall skips inactive anchors while
                // building the effects.
                if (pr.initialized && !use.gameObject.activeInHierarchy)
                {
                    d.gameObject.SetActive(false);
                    continue;
                }

                // Position comes from the model emitter (they carry real local coordinates),
                // direction comes from the command axis: exhaust always leaves along the
                // opposite of the commanded thrust, so the plume stays axis aligned and
                // predictable no matter which emitter it uses.
                Vector3 local = space.InverseTransformPoint(use.position);

                d.gameObject.SetActive(true);
                d.localPosition = local;
                d.localRotation = Quaternion.FromToRotation(Vector3.up, SlotAxis(slot));
                d.localScale = Vector3.one;
            }
        }

        // ---------------- helpers ----------------

        static int ActiveFxTotal(Part p)
        {
            int total = 0;
            PartModuleList mods = p.Modules;
            if (mods == null) return 0;
            for (int i = 0; i < mods.Count; i++)
            {
                PartModule pm = mods[i];
                if (pm == null || pm.GetType().Name != "ModuleWaterfallFX") continue;
                int c = CountOf(pm, "activeFX");
                if (c > 0) total += c;
            }
            return total;
        }

        static object GetMember(object o, string name)
        {
            if (o == null) return null;
            Type t = o.GetType();
            FieldInfo f = t.GetField(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (f != null) { try { return f.GetValue(o); } catch (Exception) { return null; } }
            PropertyInfo pi = t.GetProperty(name, BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (pi != null) { try { return pi.GetValue(o, null); } catch (Exception) { return null; } }
            return null;
        }

        static int CountOf(object o, string name)
        {
            ICollection c = GetMember(o, name) as ICollection;
            return c == null ? -1 : c.Count;
        }

        static List<PartModule> FindWaterfallModules(Part p)
        {
            List<PartModule> result = new List<PartModule>();
            PartModuleList mods = p.Modules;
            if (mods == null) return result;
            for (int i = 0; i < mods.Count; i++)
            {
                PartModule pm = mods[i];
                if (pm == null) continue;
                if (pm.GetType().Name == "ModuleWaterfallFX") result.Add(pm);
            }
            return result;
        }

        static int SuppressGasJets(Part p)
        {
            int n = 0;
            ParticleSystem[] all = p.GetComponentsInChildren<ParticleSystem>(true);
            for (int i = 0; i < all.Length; i++)
            {
                ParticleSystem ps = all[i];
                if (ps == null || ps.gameObject == null) continue;
                if (ps.gameObject.name.IndexOf("fx_gasJet", StringComparison.Ordinal) != 0) continue;
                try
                {
                    ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
                    ParticleSystem.EmissionModule em = ps.emission;
                    em.enabled = false;
                }
                catch (Exception) { }
                n++;
            }
            return n;
        }
    }
}
